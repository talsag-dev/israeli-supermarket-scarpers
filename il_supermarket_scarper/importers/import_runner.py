"""Import runner for parsing and importing supermarket data."""
import os
from pathlib import Path
from typing import Dict, List, Optional

from il_supermarket_scarper.parsers_factory import ParserFactory
from il_supermarket_scarper.utils.loop import execute_in_parallel
from il_supermarket_scarper.utils.logger import Logger
from .mongo_importer import MongoImporter


class ImportRunner:
    """Orchestrate parsing and importing of supermarket data."""

    def __init__(self, dumps_folder: str = './dumps', database_name: str = 'supermarket_data', max_workers: int = 4):
        """Initialize import runner.

        Args:
            dumps_folder: Path to dumps folder containing XML files
            database_name: MongoDB database name
            max_workers: Maximum number of parallel workers for parsing XML files
        """
        self.dumps_folder = dumps_folder
        self.importer = MongoImporter(database_name)
        self.max_workers = max_workers

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

    def import_provider(self, provider_name: str, clear_existing: bool = False) -> Dict[str, int]:
        """Import all data for a specific provider.

        Args:
            provider_name: Provider name (e.g., "SuperPharm")
            clear_existing: If True, clear existing data for this provider first

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

        # Parse files in parallel using existing execute_in_parallel utility
        stores_count = 0
        prices_count = 0
        promotions_count = 0

        # Create list of (xml_path, parser) tuples for parallel execution
        parse_args = [(xml_path, parser) for xml_path in xml_files]

        # Parse all files in parallel with automatic logging
        results = execute_in_parallel(
            lambda args: self._parse_file(*args),
            parse_args,
            max_threads=self.max_workers
        )

        # Process results
        for xml_path, (file_type, data) in zip(xml_files, results):
            xml_file = os.path.basename(xml_path)

            try:
                if file_type == 'stores' and data:
                    count = self.importer.import_stores(data)
                    stores_count += count
                    Logger.info(f"✓ {xml_file}: {count} stores")

                elif file_type == 'prices' and data:
                    count = self.importer.import_prices(data)
                    prices_count += count
                    Logger.info(f"✓ {xml_file}: {count} prices")

                elif file_type == 'promotions' and data:
                    count = self.importer.import_promotions(data)
                    promotions_count += count
                    Logger.info(f"✓ {xml_file}: {count} promotions")

                elif file_type == 'unknown':
                    Logger.warning(f"{xml_file}: unknown file type")

                elif file_type == 'error':
                    Logger.error(f"{xml_file}: {data}")  # data contains error message

            except NotImplementedError as e:
                Logger.error(f"{xml_file}: {e}")
                raise
            except Exception as e:
                Logger.error(f"{xml_file}: Error - {e}")
                # Continue with other files

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

    def import_all(self, implemented_only: bool = False) -> Dict[str, Dict[str, int]]:
        """Import data from all providers.

        Args:
            implemented_only: If True, only import fully implemented parsers

        Returns:
            Dictionary mapping provider names to their import counts
        """
        results = {}

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

    def create_indexes(self):
        """Create MongoDB indexes."""
        self.importer.create_indexes()

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics.

        Returns:
            Dictionary with counts
        """
        return self.importer.get_stats()

    def close(self):
        """Close database connection."""
        self.importer.close()
