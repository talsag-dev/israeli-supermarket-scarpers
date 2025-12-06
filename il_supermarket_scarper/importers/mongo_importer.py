"""MongoDB importer for parsed supermarket data."""
import os
from datetime import datetime
from typing import Dict, List

from il_supermarket_scarper.utils.databases.mongo import MongoDataBase, PYMONGO_INSTALLED
from il_supermarket_scarper.utils.logger import Logger

if PYMONGO_INSTALLED:
    import pymongo
    from pymongo import UpdateOne


class MongoImporter:
    """Import parsed data into MongoDB using existing MongoDataBase class."""

    def __init__(self, database_name: str = "supermarket_data"):
        """Initialize MongoDB importer.

        Args:
            database_name: Name of the MongoDB database to use
        """
        self.database_name = database_name
        self.db = MongoDataBase(database_name)
        self.db.enable_collection_status()

        if not PYMONGO_INSTALLED:
            raise ImportError("PyMongo is not installed. Please install it to use MongoDB importer.")

        if not self.db.is_collection_enabled():
            raise RuntimeError("Failed to connect to MongoDB.")

    def create_indexes(self):
        """Create MongoDB indexes for efficient querying."""
        if not self.db.is_collection_enabled():
            return

        # Stores collection indexes
        self.db.store_db['stores'].create_index(
            [('provider', pymongo.ASCENDING), ('store_id', pymongo.ASCENDING)],
            unique=True,
            name='idx_provider_store_id'
        )
        self.db.store_db['stores'].create_index(
            [('city', pymongo.ASCENDING)],
            name='idx_city'
        )
        self.db.store_db['stores'].create_index(
            [('chain_id', pymongo.ASCENDING)],
            name='idx_chain_id'
        )

        # Prices collection indexes
        self.db.store_db['prices'].create_index(
            [('provider', pymongo.ASCENDING), ('store_id', pymongo.ASCENDING), ('item_code', pymongo.ASCENDING)],
            unique=True,
            name='idx_provider_store_item'
        )
        self.db.store_db['prices'].create_index(
            [('item_code', pymongo.ASCENDING)],
            name='idx_item_code'
        )
        self.db.store_db['prices'].create_index(
            [('item_name', pymongo.TEXT)],
            name='idx_item_name_text'
        )
        self.db.store_db['prices'].create_index(
            [('price_update_date', pymongo.DESCENDING)],
            name='idx_price_update_date'
        )

        # Promotions collection indexes
        self.db.store_db['promotions'].create_index(
            [('provider', pymongo.ASCENDING), ('store_id', pymongo.ASCENDING), ('promotion_id', pymongo.ASCENDING)],
            unique=True,
            name='idx_provider_store_promo'
        )
        self.db.store_db['promotions'].create_index(
            [('item_code', pymongo.ASCENDING)],
            name='idx_promo_item_code'
        )
        self.db.store_db['promotions'].create_index(
            [('promotion_start_date', pymongo.ASCENDING)],
            name='idx_promo_start_date'
        )
        self.db.store_db['promotions'].create_index(
            [('promotion_end_date', pymongo.ASCENDING)],
            name='idx_promo_end_date'
        )

        Logger.info("✓ MongoDB indexes created successfully")

    def import_stores(self, stores: List[Dict], batch_size: int = 1000) -> int:
        """Import stores with BULK UPSERT by (provider, store_id).

        Args:
            stores: List of store dictionaries
            batch_size: Number of documents to process in each batch

        Returns:
            Number of stores imported
        """
        if not self.db.is_collection_enabled() or not stores:
            return 0

        imported_at = datetime.utcnow()
        total_count = 0

        # Process in batches for better performance
        for i in range(0, len(stores), batch_size):
            batch = stores[i:i + batch_size]
            operations = []

            for store in batch:
                store['imported_at'] = imported_at

                # Build bulk upsert operation
                operations.append(
                    UpdateOne(
                        {'provider': store['provider'], 'store_id': store['store_id']},
                        {'$set': store},
                        upsert=True
                    )
                )

            # Execute bulk write
            if operations:
                try:
                    result = self.db.store_db['stores'].bulk_write(operations, ordered=False)
                    total_count += result.upserted_count + result.modified_count
                    Logger.info(f"Batch {i//batch_size + 1}: {len(operations)} stores processed")
                except Exception as e:
                    Logger.error(f"Error in batch {i//batch_size + 1}: {e}")

        return total_count

    def import_prices(self, prices: List[Dict], batch_size: int = 1000) -> int:
        """Import prices with BULK UPSERT by (provider, store_id, item_code).

        Args:
            prices: List of price dictionaries
            batch_size: Number of documents to process in each batch

        Returns:
            Number of prices imported
        """
        if not self.db.is_collection_enabled() or not prices:
            return 0

        imported_at = datetime.utcnow()
        total_count = 0

        # Process in batches for better performance
        for i in range(0, len(prices), batch_size):
            batch = prices[i:i + batch_size]
            operations = []

            for price in batch:
                price['imported_at'] = imported_at

                # Build bulk upsert operation
                operations.append(
                    UpdateOne(
                        {
                            'provider': price['provider'],
                            'store_id': price['store_id'],
                            'item_code': price['item_code']
                        },
                        {'$set': price},
                        upsert=True
                    )
                )

            # Execute bulk write
            if operations:
                try:
                    result = self.db.store_db['prices'].bulk_write(operations, ordered=False)
                    total_count += result.upserted_count + result.modified_count
                    Logger.info(f"Batch {i//batch_size + 1}: {len(operations)} prices processed")
                except Exception as e:
                    Logger.error(f"Error in batch {i//batch_size + 1}: {e}")

        return total_count

    def import_promotions(self, promotions: List[Dict], batch_size: int = 1000) -> int:
        """Import promotions with BULK UPSERT by (provider, store_id, promotion_id).

        Args:
            promotions: List of promotion dictionaries
            batch_size: Number of documents to process in each batch

        Returns:
            Number of promotions imported
        """
        if not self.db.is_collection_enabled() or not promotions:
            return 0

        imported_at = datetime.utcnow()
        total_count = 0

        # Process in batches for better performance
        for i in range(0, len(promotions), batch_size):
            batch = promotions[i:i + batch_size]
            operations = []

            for promo in batch:
                promo['imported_at'] = imported_at

                # Build bulk upsert operation
                operations.append(
                    UpdateOne(
                        {
                            'provider': promo['provider'],
                            'store_id': promo['store_id'],
                            'promotion_id': promo['promotion_id']
                        },
                        {'$set': promo},
                        upsert=True
                    )
                )

            # Execute bulk write
            if operations:
                try:
                    result = self.db.store_db['promotions'].bulk_write(operations, ordered=False)
                    total_count += result.upserted_count + result.modified_count
                    Logger.info(f"Batch {i//batch_size + 1}: {len(operations)} promotions processed")
                except Exception as e:
                    Logger.error(f"Error in batch {i//batch_size + 1}: {e}")

        return total_count

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics.

        Returns:
            Dictionary with counts of stores, prices, and promotions
        """
        if not self.db.is_collection_enabled():
            return {'stores': 0, 'prices': 0, 'promotions': 0}

        return {
            'stores': self.db.store_db['stores'].count_documents({}),
            'prices': self.db.store_db['prices'].count_documents({}),
            'promotions': self.db.store_db['promotions'].count_documents({})
        }

    def clear_provider_data(self, provider: str):
        """Clear all data for a specific provider.

        Args:
            provider: Provider name to clear
        """
        if not self.db.is_collection_enabled():
            return

        self.db.store_db['stores'].delete_many({'provider': provider})
        self.db.store_db['prices'].delete_many({'provider': provider})
        self.db.store_db['promotions'].delete_many({'provider': provider})
        Logger.info(f"✓ Cleared all data for provider: {provider}")

    def close(self):
        """Close MongoDB connection."""
        if self.db.myclient:
            self.db.myclient.close()
