import os
import openai
from typing import Dict, Any, Optional, List
from il_supermarket_scarper.utils.logger import Logger

class LLMEngine:
    """Engine for handling LLM interactions (Text-to-SQL) with RAG capabilities."""

    # Geographic region mapping for Israeli regions
    REGION_MAPPING = {
        'מרכז': ['תל אביב-יפו', 'תל אביב', 'רמת גן', 'גבעתיים', 'בני ברק', 'חולון', 
                 'בת ים', 'ראשון לציון', 'רחובות', 'נס ציונה', 'פתח תקווה', 
                 'הרצליה', 'רעננה', 'כפר סבא', 'הוד השרון', 'רמת השרון', 'לוד', 'רמלה'],
        'צפון': ['חיפה', 'נצרת', 'עכו', 'טבריה', 'צפת', 'קריית שמונה', 'נהריה', 
                 'כרמיאל', 'קריית ביאליק', 'קריית מוצקין', 'קריית ים', 'עפולה'],
        'דרום': ['באר שבע', 'אשדוד', 'אשקלון', 'אילת', 'דימונה', 'קריית גת', 
                 'נתיבות', 'אופקים', 'שדרות', 'ערד'],
        'ירושלים': ['ירושלים', 'בית שמש', 'מעלה אדומים', 'מודיעין', 'מודיעין-מכבים-רעות'],
        'שרון': ['נתניה', 'רעננה', 'כפר סבא', 'הוד השרון', 'הרצליה', 'רמת השרון'],
        'שפלה': ['רחובות', 'נס ציונה', 'ראשון לציון', 'לוד', 'רמלה', 'קריית גת']
    }

    BASE_SCHEMA_CONTEXT = """
    You are an expert ClickHouse SQL assistant for a supermarket price comparison database.
    
    Database Schema:
    
    1. Table 'supermarket_data.stores':
       - ChainId (String): Chain identifier
       - StoreId (Int32): Store identifier
       - StoreName (String): Name of the store
       - City (String): City name
       - Address (String): Store address
       - ZipCode (String): Postal code
    
    2. Table 'supermarket_data.prices':
       - ChainId, StoreId (String, Int32): Link to stores
       - ItemName (String): Name of the product (e.g., 'במבה', 'חלב 3%')
       - ItemPrice (Float32): Price of the item
       - ManufacturerName (String): Manufacturer
       - ItemCode (String): Barcode/Item ID
       - Quantity (Float32): Amount
       - UnitQty (String): Unit name (e.g., '1 ליטר')
       - LastUpdate (DateTime): When it was scraped
        
    3. Table 'supermarket_data.promotions':
       - PromotionDescription (String): Description of the deal
       - PromotionStartDate, PromotionEndDate (DateTime): Promotion period
    
    Rules:
    - Return ONLY the raw SQL query. No markdown, no explanations.
    - Use ClickHouse syntax (e.g., `LIMIT 10` is good).
    - Use `ilike` for case-insensitive partial matches on names (e.g. `ItemName ilike '%במבה%'`).
    - The date column is `LastUpdate`.
    - ALWAYS use fully qualified table names: `supermarket_data.stores`, `supermarket_data.prices`
    - ALWAYS limit results to 100 rows maximum unless asked otherwise.
    - When joining stores and prices, use: `JOIN supermarket_data.stores s ON p.ChainId = s.ChainId AND p.StoreId = s.StoreId`
    
    SEARCH SPECIFICITY:
    - When searching for products, be SPECIFIC to avoid irrelevant results.
    - For common products like "milk" (חלב), "bread" (לחם), etc., use word boundaries or exact matches when possible.
    - Example: Instead of `ItemName ilike '%חלב%'` which matches "חלבון" (protein), 
      use `ItemName ilike '%חלב %' OR ItemName ilike '% חלב%' OR ItemName = 'חלב'` to match actual milk products.
    - For brand names like "במבה" or "ביסלי", exact partial match is fine: `ItemName ilike '%במבה%'`
    - If user asks for a specific product category, try to filter more precisely to avoid unrelated items.
    - Consider using ORDER BY ItemPrice ASC or similar to show most relevant/useful results first.
    
    CONVERSATION CONTEXT:
    - If there is conversation history, pay close attention to previous questions and queries.
    - Follow-up questions like "in Tel Aviv?" or "what about in the center?" should BUILD UPON the previous query.
    - Maintain filters from previous queries (e.g., if user asked about "milk", keep filtering for milk in follow-ups).
    - If the user adds a location filter, ADD it to the existing query, don't replace the entire query.
    - Example: If previous query was about "milk products", and user asks "in Tel Aviv?", 
      generate SQL that filters for BOTH milk products AND Tel Aviv location.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            Logger.warning("OPENAI_API_KEY not found. LLM features will fail.")
        else:
            openai.api_key = self.api_key

    def _preprocess_query(self, question: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Preprocess query to expand region names and add context."""
        processed = question
        region_detected = None
        
        # Check if question mentions a region
        for region, cities in self.REGION_MAPPING.items():
            if region in question:
                region_detected = region
                # Build explicit instruction for LLM
                cities_list = "', '".join(cities)
                instruction = f"""

IMPORTANT INSTRUCTION: The user mentioned '{region}' which is a REGION, not a city name.
You MUST use this SQL pattern to search in the {region} region:
s.City IN ('{cities_list}')

DO NOT use: s.City ilike '%{region}%'
INSTEAD use: s.City IN ('{cities_list}')
"""
                processed += instruction
                Logger.info(f"Detected region '{region}' in query, added explicit city IN clause instruction")
                break
        
        return processed

    def _build_dynamic_context(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Build dynamic schema context with actual database metadata."""
        context = self.BASE_SCHEMA_CONTEXT
        
        if metadata:
            context += "\n\nDatabase Content Information:\n"
            
            # Add available cities
            if metadata.get("cities"):
                cities = metadata["cities"][:20]  # Limit to first 20 cities
                context += f"\nAvailable cities (sample): {', '.join(cities)}\n"
            
            # Add chain information
            if metadata.get("chains"):
                chains = [f"{c['chain_id']} ({c['store_count']} stores)" 
                         for c in metadata["chains"][:5]]
                context += f"\nAvailable chains: {', '.join(chains)}\n"
            
            # Add stats
            if metadata.get("stats"):
                stats = metadata["stats"]
                context += f"\nDatabase stats: {stats.get('stores', 0)} stores, {stats.get('prices', 0)} price records\n"
        
        return context

    def generate_sql(self, user_question: str, metadata: Optional[Dict[str, Any]] = None, 
                     conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Convert natural language to SQL with RAG-enhanced context and conversation history.
        
        Args:
            user_question: The current user question
            metadata: Database metadata for RAG context
            conversation_history: List of previous messages in format [{"role": "user"|"assistant", "content": "..."}]
        """
        if not self.api_key:
            raise ValueError("OpenAI API Key is missing.")

        try:
            # Preprocess query to expand regions
            processed_question = self._preprocess_query(user_question, metadata)
            
            # Build dynamic context with metadata
            schema_context = self._build_dynamic_context(metadata)
            
            # Build message history for OpenAI
            messages = [{"role": "system", "content": schema_context}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
                Logger.info(f"Generating SQL with {len(conversation_history)} previous messages")
            
            # Add current question
            messages.append({"role": "user", "content": f"Question: {processed_question}"})
            
            Logger.info(f"Generating SQL with RAG context (metadata: {bool(metadata)}, history: {bool(conversation_history)})")
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.0
            )
            
            sql = response.choices[0].message.content.strip()
            # Clean possible markdown code blocks
            sql = sql.replace("```sql", "").replace("```", "").strip()
            return sql
            
        except Exception as e:
            Logger.error(f"LLM Generation Failed: {e}")
            raise
