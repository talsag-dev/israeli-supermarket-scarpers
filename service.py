from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from il_supermarket_scarper import ScarpingTask
from il_supermarket_scarper.importers.import_runner import ImportRunner
from il_supermarket_scarper.utils.logger import Logger
from il_supermarket_scarper.engines.llm_engine import LLMEngine
from il_supermarket_scarper.importers.clickhouse_importer import ClickHouseImporter
import threading
import os

# Global instances
llm_engine = LLMEngine()
clickhouse_client = ClickHouseImporter(database_name='supermarket_data')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Logger.info("Starting up service...")
    yield
    # Shutdown
    Logger.info("Shutting down service...")

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lock to prevent multiple concurrent runs
scrape_lock = threading.Lock()
import_lock = threading.Lock()

def run_scraper_task():
    """Run the scraper task."""
    if not scrape_lock.acquire(blocking=False):
        Logger.info("Scraper is already running, skipping.")
        return

    try:
        Logger.info("Starting Scraper from Service...")
        # ScarpingTask reads env vars automatically
        scraper = ScarpingTask()
        scraper.start()
        Logger.info("Scraper finished successfully.")
    except Exception as e:
        Logger.error(f"Scraper failed: {e}")
    finally:
        scrape_lock.release()

def run_import_task():
    """Run the import task."""
    if not import_lock.acquire(blocking=False):
        Logger.info("Importer is already running, skipping.")
        return

    try:
        Logger.info("Starting Importer from Service...")
        runner = ImportRunner(dumps_folder=os.getenv("DUMPS_FOLDER", "./dumps"))
        runner.import_all(implemented_only=True, fast_mode=True)
        runner.close()
        Logger.info("Importer finished successfully.")
    except Exception as e:
        Logger.error(f"Importer failed: {e}")
    finally:
        import_lock.release()

@app.get("/health")
def health_check():
    return {"status": "ok"}

class QueryRequest(BaseModel):
    question: str
    conversation_history: list = []  # List of {role: "user"|"assistant", content: str}

@app.post("/query")
async def query_data(request: QueryRequest, debug: bool = False):
    """
    Convert natural language question to SQL and execute it against ClickHouse.
    Uses RAG to provide database metadata context to the LLM.
    Supports conversation history for contextual follow-up questions.
    
    Args:
        request: Query request with user question and optional conversation history
        debug: If True, returns metadata context used for generation
    """
    try:
        # 1. Retrieve database metadata for RAG context
        Logger.info("Retrieving database metadata for RAG context...")
        metadata = clickhouse_client.get_metadata_summary()
        
        # 2. Generate SQL with metadata context and conversation history
        sql_query = llm_engine.generate_sql(
            request.question, 
            metadata=metadata,
            conversation_history=request.conversation_history
        )
        Logger.info(f"Generated SQL: {sql_query}")

        # 3. Execute SQL
        result = clickhouse_client.client.query(sql_query)

        response = {
            "question": request.question,
            "sql": sql_query,
            "data": result.result_rows,
            "columns": result.column_names
        }
        
        # Include metadata in debug mode
        if debug:
            response["metadata"] = {
                "cities_count": len(metadata.get("cities", [])),
                "chains_count": len(metadata.get("chains", [])),
                "sample_cities": metadata.get("cities", [])[:10],
                "stats": metadata.get("stats", {})
            }
        
        return response
    except Exception as e:
        Logger.error(f"Query processing error: {e}")
        return {"error": str(e)}

@app.post("/scrape")
def trigger_scrape(background_tasks: BackgroundTasks):
    """Trigger the scraper in the background."""
    if scrape_lock.locked():
        raise HTTPException(status_code=409, detail="Scraper is already running")

    background_tasks.add_task(run_scraper_task)
    return {"message": "Scraper started in background"}

@app.post("/import")
def trigger_import(background_tasks: BackgroundTasks):
    """Trigger the importer in the background."""
    if import_lock.locked():
        raise HTTPException(status_code=409, detail="Importer is already running")

    background_tasks.add_task(run_import_task)
    return {"message": "Importer started in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
