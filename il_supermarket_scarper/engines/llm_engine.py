import os
import openai
from typing import Dict, Any, Optional
from il_supermarket_scarper.utils.logger import Logger

class LLMEngine:
    """Engine for handling LLM interactions (Text-to-SQL)."""

    SCHEMA_CONTEXT = """
    You are an expert ClickHouse SQL assistant for a supermarket price comparison database.
    
    Database Schema:
    
    1. Table 'stores':
       - ChainId (String): Chain identifier
       - StoreId (Int32): Store identifier
       - StoreName (String): Name of the store
       - City (String): City name
    
    2. Table 'prices':
       - ChainId, StoreId (String, Int32): Link to stores
       - ItemName (String): Name of the product (e.g., 'Milk 3%')
       - ItemPrice (Float32): Price of the item
       - ManufacturerName (String): Manufacturer
       - ItemCode (String): Barcode/Item ID
       - Quantity (Float32): Amount
       - UnitQty (String): Unit name (e.g., '1 Litre')
       - LastUpdate (DateTime): When it was scraped
       
    3. Table 'promotions':
       - PromotionDescription (String): Description of the deal
       - DiscountRate (Float32): Discount percentage
       - DiscountedPrice (Float32): Price after discount
    
    Rules:
    - Return ONLY the raw SQL query. No markdown, no explanations.
    - Use ClickHouse syntax (e.g., `LIMIT 10` is good).
    - Use `ilike` for case-insensitive partial matches on names (e.g. `ItemName ilike '%milk%'`).
    - The date column is `LastUpdate`.
    - ALWAYS limit results to 100 rows maximum unless asked otherwise.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            Logger.warning("OPENAI_API_KEY not found. LLM features will fail.")
        else:
            openai.api_key = self.api_key

    def generate_sql(self, user_question: str) -> str:
        """Convert natural language to SQL."""
        if not self.api_key:
            raise ValueError("OpenAI API Key is missing.")

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.SCHEMA_CONTEXT},
                    {"role": "user", "content": f"Question: {user_question}"}
                ],
                temperature=0.0
            )
            
            sql = response.choices[0].message.content.strip()
            # Clean possible markdown code blocks
            sql = sql.replace("```sql", "").replace("```", "").strip()
            return sql
            
        except Exception as e:
            Logger.error(f"LLM Generation Failed: {e}")
            raise
