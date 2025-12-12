"""Import runner for parsing and importing supermarket data."""
import os
from pathlib import Path
from typing import Dict, List, Optional
from il_supermarket_scarper.parsers_factory import ParserFactory
from il_supermarket_scarper.utils.loop import execute_in_parallel
from il_supermarket_scarper.utils.logger import Logger


class ImportRunner:
    """Orchestrate parsing and importing of supermarket data."""

    def __init__(self, dumps_folder: str = './dumps', database_name: str = 'supermarket_data', max_workers: int = 4):
        """Initialize import runner.

        Args:
            dumps_folder: Path to dumps folder containing XML files
            database_name: Database name
            max_workers: Maximum number of parallel workers for parsing XML files
        """
        self.dumps_folder = dumps_folder
        
        # Determine max_workers from env if not explicit, else use default/arg
        env_mw = os.getenv('MAX_WORKERS')
        if env_mw:
            self.max_workers = int(env_mw)
        else:
            self.max_workers = max_workers

        from .clickhouse_importer import ClickHouseImporter
        self.importer = ClickHouseImporter(database_name)
        Logger.info("Using ClickHouse Importer")

    def _parse_file(self, xml_path: str, parser) -> tuple:
        """Parse a single XML file.

        Args:
            xml_path: Path to XML file
            parser: Parser instance to use

        Returns:
            Tuple of (file_type, parsed_data) or (file_type, error_message)
        """
        xml_file = os.path.basename(xml_path)

        try:
            file_type = parser.detect_file_type(xml_file)

            if file_type == 'stores':
                data = parser.parse_stores(xml_path)
            elif file_type == 'prices':
                data = parser.parse_prices(xml_path)
            elif file_type == 'promotions':
                data = parser.parse_promotions(xml_path)
            else:
                data = None
                file_type = 'unknown'

            return file_type, data

        except Exception as e:
            # Return error info so it can be handled in main thread
            return 'error', str(e)

    def import_provider(self, provider_name: str, clear_existing: bool = False, batch_size: int = 50) -> Dict[str, int]:
        """Import all data for a specific provider.

        Args:
            provider_name: Provider name (e.g., "SuperPharm")
            clear_existing: If True, clear existing data for this provider first
            batch_size: Number of files to process in each batch

        Returns:
            Dictionary with counts of imported stores, prices, promotions

        Raises:
            ValueError: If provider parser not found
            NotImplementedError: If provider parser is a skeleton
        """
        # Get parser
        parser = ParserFactory.get_parser(provider_name)
        if parser is None:
            raise ValueError(f"Parser not found for provider: {provider_name}")

        Logger.info(f"\n=== Importing {provider_name} ===")

        # Clear existing data if requested
        if clear_existing:
            self.importer.clear_provider_data(provider_name)

        # Find provider folder in dumps
        provider_folder = os.path.join(self.dumps_folder, provider_name)
        if not os.path.exists(provider_folder):
            Logger.warning(f"Dumps folder not found for {provider_name}: {provider_folder}")
            return {'stores': 0, 'prices': 0, 'promotions': 0}

        # Collect all XML files
        xml_files = [
            os.path.join(provider_folder, f)
            for f in os.listdir(provider_folder)
            if f.endswith('.xml')
        ]

        if not xml_files:
            Logger.warning(f"No XML files found in {provider_folder}")
            return {'stores': 0, 'prices': 0, 'promotions': 0}

        total_files = len(xml_files)
        Logger.info(f"Found {total_files} files to import")

        stores_count = 0
        prices_count = 0
        promotions_count = 0

        # Process in batches
        for i in range(0, total_files, batch_size):
            batch_files = xml_files[i : i + batch_size]
            Logger.info(f"Processing batch {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size} ({len(batch_files)} files)...")

            # Create list of (xml_path, parser) tuples for parallel execution
            parse_args = [(xml_path, parser) for xml_path in batch_files]

            # Parse batch files in parallel
            results = execute_in_parallel(
                lambda args: self._parse_file(*args),
                parse_args,
                max_threads=self.max_workers
            )

            batch_stores = []
            batch_prices = []
            batch_promotions = []

            # Process results for this batch
            for xml_path, result_tuple in zip(batch_files, results):
                # execute_in_parallel returns results in order
                file_type, data = result_tuple
                xml_file = os.path.basename(xml_path)

                try:
                    if file_type == 'stores' and data:
                        batch_stores.extend(data)
                        Logger.info(f"✓ {xml_file}: parsed {len(data)} stores")

                    elif file_type == 'prices' and data:
                        batch_prices.extend(data)
                        Logger.info(f"✓ {xml_file}: parsed {len(data)} prices")

                    elif file_type == 'promotions' and data:
                        batch_promotions.extend(data)
                        Logger.info(f"✓ {xml_file}: parsed {len(data)} promotions")

                    elif file_type == 'unknown':
                        Logger.warning(f"{xml_file}: unknown file type")

                    elif file_type == 'error':
                        Logger.error(f"{xml_file}: {data}")

                except Exception as e:
                    Logger.error(f"{xml_file}: Error processing result - {e}")

            # Bulk import for the batch
            try:
                if batch_stores:
                    count = self.importer.import_stores(batch_stores)
                    stores_count += count
                    Logger.info(f"  -> Imported {count} stores from batch")
                
                if batch_prices:
                    count = self.importer.import_prices(batch_prices)
                    prices_count += count
                    Logger.info(f"  -> Imported {count} prices from batch")
                
                if batch_promotions:
                    count = self.importer.import_promotions(batch_promotions)
                    promotions_count += count
                    Logger.info(f"  -> Imported {count} promotions from batch")
            
            except Exception as e:
                 Logger.error(f"Error importing batch: {e}")

        result = {
            'stores': stores_count,
            'prices': prices_count,
            'promotions': promotions_count
        }

        Logger.info(f"\nTotal imported for {provider_name}:")
        Logger.info(f"  - Stores: {stores_count}")
        Logger.info(f"  - Prices: {prices_count}")
        Logger.info(f"  - Promotions: {promotions_count}")

        return result

    def import_all(self, implemented_only: bool = False, fast_mode: bool = False) -> Dict[str, Dict[str, int]]:
        """Import data from all providers.

        Args:
            implemented_only: If True, only import fully implemented parsers
            fast_mode: If True, drop indexes before import and recreate after (faster but risky)

        Returns:
            Dictionary mapping provider names to their import counts
        """
        results = {}

        if fast_mode:
            Logger.info("FAST MODE: Dropping indexes to speed up import...")
            self.importer.drop_indexes()

        if implemented_only:
            providers = ParserFactory.get_implemented_parsers()
        else:
            # Get all provider folders in dumps
            providers = self._discover_providers()

        for provider in providers:
            try:
                result = self.import_provider(provider)
                results[provider] = result
            except NotImplementedError:
                Logger.warning(f"Skipping {provider}: Parser not yet implemented")
                continue
            except Exception as e:
                Logger.error(f"Failed to import {provider}: {e}")
                continue

        Logger.info("=== All Imports Completed ===")
        Logger.info("Summary:")
        total_stores = 0
        total_prices = 0
        total_promotions = 0
        
        for provider, res in results.items():
            s = res.get('stores', 0)
            p = res.get('prices', 0)
            pro = res.get('promotions', 0)
            total_stores += s
            total_prices += p
            total_promotions += pro
            Logger.info(f"- {provider}: {s} stores, {p} prices, {pro} promos")
            
        Logger.info(f"TOTAL: {total_stores} stores, {total_prices} prices, {total_promotions} promos")

        return results

    def _discover_providers(self) -> List[str]:
        """Discover all provider folders in dumps directory.

        Returns:
            List of provider names found in dumps
        """
        if not os.path.exists(self.dumps_folder):
            return []

        providers = []
        for item in os.listdir(self.dumps_folder):
            item_path = os.path.join(self.dumps_folder, item)
            if os.path.isdir(item_path) and ParserFactory.has_parser(item):
                providers.append(item)

        return providers

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics.

        Returns:
            Dictionary with counts
        """
        return self.importer.get_stats()

    def close(self):
        """Close database connection."""
        self.importer.close()
