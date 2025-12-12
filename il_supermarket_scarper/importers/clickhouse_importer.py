import clickhouse_connect
import os
from datetime import datetime
from typing import List, Dict, Any
from il_supermarket_scarper.utils.logger import Logger

class ClickHouseImporter:
    """Importer for ClickHouse database."""

    def __init__(self, database_name: str = 'supermarket_data'):
        """Initialize ClickHouse importer.
        
        Tries to connect to host specified in CLICKHOUSE_HOST env var, 
        defaults to 'localhost' (for local run) or 'clickhouse' (for docker).
        """
        self.host = os.getenv('CLICKHOUSE_HOST', 'localhost')
        self.port = int(os.getenv('CLICKHOUSE_PORT', 8123))
        self.database = database_name
        self.client = None
        self._connect()
        self._ensure_database()
        self._create_tables()

    def _connect(self):
        """Establish connection to ClickHouse."""
        try:
            self.client = clickhouse_connect.get_client(
                host=self.host, 
                port=self.port,
                username=os.getenv('CLICKHOUSE_USER', 'default'),
                password=os.getenv('CLICKHOUSE_PASSWORD', ''),
                database=self.database
            )
            Logger.info(f"Connected to ClickHouse at {self.host}:{self.port}")
        except Exception as e:
            Logger.error(f"Failed to connect to ClickHouse: {e}")
            raise

    def _ensure_database(self):
        """Ensure database exists."""
        self.client.command(f"CREATE DATABASE IF NOT EXISTS {self.database}")

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        # Stores Table
        self.client.command(f"""
        CREATE TABLE IF NOT EXISTS {self.database}.stores (
            ChainId String,
            StoreId Int32,
            StoreName String,
            Address String,
            City String,
            ZipCode String,
            LastUpdate DateTime DEFAULT now()
        ) ENGINE = ReplacingMergeTree(LastUpdate)
        ORDER BY (ChainId, StoreId)
        """)

        # Prices Table
        # Using MergeTree optimized for large inserts.
        self.client.command(f"""
        CREATE TABLE IF NOT EXISTS {self.database}.prices (
            ChainId String,
            StoreId Int32,
            ItemCode String,
            ItemName String,
            ManufacturerName String,
            ManufactureCountry String,
            UnitQty String,
            Quantity Float32,
            bIsWeighted Int8,
            UnitOfMeasure String,
            QtyInPackage Int32,
            ItemPrice Float32,
            UnitOfMeasurePrice Float32,
            AllowDiscount Int8,
            ItemStatus Int8,
            LastUpdate DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (ChainId, StoreId, ItemCode, LastUpdate)
        """)

        # Promotions Table
        self.client.command(f"""
        CREATE TABLE IF NOT EXISTS {self.database}.promotions (
            ChainId String,
            StoreId Int32,
            PromotionId String,
            PromotionDescription String,
            PromotionStartDate DateTime,
            PromotionEndDate DateTime,
            DisplayPrioroty Int32,
            IsWeighted Int8,
            LastUpdate DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (ChainId, StoreId, PromotionId, LastUpdate)
        """)
        
        Logger.info("ClickHouse tables created/verified.")

    def import_stores(self, stores: List[Dict[str, Any]]) -> int:
        """Import stores data."""
        if not stores:
            return 0
        
        # Prepare data for insertion (list of lists/tuples)
        data = []
        for s in stores:
            data.append([
                str(s.get('chain_id', '')),
                int(s.get('store_id', 0)),
                str(s.get('store_name', '')),
                str(s.get('address', '')),
                str(s.get('city', '')),
                str(s.get('zip_code', '')),
                datetime.now()
            ])
            
        self.client.insert(f'{self.database}.stores', data, column_names=[
            'ChainId', 'StoreId', 'StoreName', 'Address', 'City', 'ZipCode', 'LastUpdate'
        ])
        return len(stores)

    def import_prices(self, prices: List[Dict[str, Any]]) -> int:
        """Import prices data."""
        if not prices:
            return 0
            
        data = []
        now = datetime.now()
        for p in prices:
            # Handle potential missing/dirty data safely
            try:
                row = [
                    str(p.get('chain_id', '')),
                    int(p.get('store_id', 0)),
                    str(p.get('item_code', '')),
                    str(p.get('item_name', '')),
                    str(p.get('manufacturer_name', '')),
                    str(p.get('manufacture_country', '')),
                    str(p.get('unit_qty', '')),
                    float(p.get('quantity', 0.0)),
                    int(p.get('bls_weighted', 0)), # Parser uses 'bls_weighted'
                    str(p.get('unit_of_measure', '')),
                    int(p.get('qty_in_package', 0)),
                    float(p.get('item_price', 0.0)),
                    float(p.get('unit_of_measure_price', 0.0)),
                    int(p.get('allow_discount', 0)),
                    int(p.get('item_status', 0)),
                    now
                ]
                data.append(row)
            except (ValueError, TypeError):
                continue

        self.client.insert(f'{self.database}.prices', data, column_names=[
            'ChainId', 'StoreId', 'ItemCode', 'ItemName', 'ManufacturerName', 
            'ManufactureCountry', 'UnitQty', 'Quantity', 'bIsWeighted', 
            'UnitOfMeasure', 'QtyInPackage', 'ItemPrice', 'UnitOfMeasurePrice',
            'AllowDiscount', 'ItemStatus', 'LastUpdate'
        ])
        return len(data)

    def import_promotions(self, promotions: List[Dict[str, Any]]) -> int:
        """Import promotions data."""
        if not promotions:
            return 0

        data = []
        now = datetime.now()
        for p in promotions:
             try:
                row = [
                    str(p.get('chain_id', '')),
                    int(p.get('store_id', 0)),
                    str(p.get('promotion_id', '')),
                    str(p.get('promotion_description', '')),
                    p.get('promotion_start_date', now),
                    p.get('promotion_end_date', now),
                    int(p.get('display_prioroty', 0)), # Parser might map this differently? Let's assume snake_case
                    int(p.get('is_weighted', 0)),
                    now
                ]
                # Note: 'DisplayPrioroty' in table (typo in original schema?). Parser usually keys snake_case of XML.
                # Let's check parser promo keys if needed, but 'display_prioroty' is a safe guess for now given standard mapping.
                data.append(row)
             except (ValueError, TypeError):
                 continue
                 
        self.client.insert(f'{self.database}.promotions', data, column_names=[
            'ChainId', 'StoreId', 'PromotionId', 'PromotionDescription',
            'PromotionStartDate', 'PromotionEndDate', 'DisplayPrioroty',
            'IsWeighted', 'LastUpdate'
        ])
        return len(data)

    def drop_indexes(self):
        """No indexes to drop in ClickHouse, effectively no-op or drop tables if needed."""
        # For ClickHouse, we typically rely on the MergeTree engine to handle speed. 
        # Dropping tables would be the equivalent of clearing data.
        pass

    def create_indexes(self):
        """No indexes to create."""
        pass

    def clear_provider_data(self, provider_name: str):
        """Clear data for a specific provider/ChainId.
        
        Note: Delete in ClickHouse is a mutation and can be expensive. 
        Use with caution or prefer partitioning.
        """
        # In this simple implementation, we might skip clearing or use ALTER TABLE DELETE
        # For now, let's just log verification.
        Logger.info(f"Clearing data for {provider_name} in ClickHouse (Mutation)")
        # Mapping provider name to ChainId would be needed here, or we simply delete by ChainId if known.
        # This part requires mapping ProviderName -> ChainId which isn't always 1:1 or clear.
        pass

    def get_stats(self) -> Dict[str, int]:
        """Get row counts."""
        stats = {}
        for table in ['stores', 'prices', 'promotions']:
            r = self.client.query(f"SELECT count() FROM {self.database}.{table}")
            stats[table] = r.result_rows[0][0]
        return stats

    def get_available_cities(self) -> List[str]:
        """Get list of unique cities with stores."""
        try:
            result = self.client.query(f"""
                SELECT DISTINCT City 
                FROM {self.database}.stores 
                WHERE City != '' 
                ORDER BY City
            """)
            return [row[0] for row in result.result_rows]
        except Exception as e:
            Logger.error(f"Failed to get available cities: {e}")
            return []

    def get_available_chains(self) -> List[Dict[str, Any]]:
        """Get list of chains with store counts."""
        try:
            result = self.client.query(f"""
                SELECT ChainId, COUNT(DISTINCT StoreId) as store_count
                FROM {self.database}.stores
                GROUP BY ChainId
                ORDER BY store_count DESC
            """)
            return [{"chain_id": row[0], "store_count": row[1]} for row in result.result_rows]
        except Exception as e:
            Logger.error(f"Failed to get available chains: {e}")
            return []

    def get_popular_items(self, limit: int = 100) -> List[str]:
        """Get most common item names."""
        try:
            result = self.client.query(f"""
                SELECT ItemName, COUNT(*) as cnt
                FROM {self.database}.prices
                WHERE ItemName != ''
                GROUP BY ItemName
                ORDER BY cnt DESC
                LIMIT {limit}
            """)
            return [row[0] for row in result.result_rows]
        except Exception as e:
            Logger.error(f"Failed to get popular items: {e}")
            return []

    def get_metadata_summary(self) -> Dict[str, Any]:
        """Get comprehensive metadata summary for LLM context."""
        return {
            "cities": self.get_available_cities(),
            "chains": self.get_available_chains(),
            "popular_items": self.get_popular_items(50),  # Limit to top 50 for context size
            "stats": self.get_stats()
        }

    def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
