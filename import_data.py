#!/usr/bin/env python3
"""
CLI tool to import scraped supermarket data into MongoDB.

Usage:
    python import_data.py --provider SuperPharm
    python import_data.py --all
    python import_data.py --implemented  # Only import fully implemented parsers
    python import_data.py --list-parsers
    python import_data.py --stats
    python import_data.py --create-indexes
"""

import argparse
import sys

from il_supermarket_scarper.importers import ImportRunner, MongoImporter
from il_supermarket_scarper.parsers_factory import ParserFactory


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Import supermarket XML data to MongoDB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all parsers (34 total)
  python import_data.py --list-parsers

  # Import specific provider
  python import_data.py --provider SuperPharm

  # Import only implemented parsers (SuperPharm, Shufersal, Victory)
  python import_data.py --implemented

  # Import all providers
  python import_data.py --all

  # Show database statistics
  python import_data.py --stats

  # Create MongoDB indexes
  python import_data.py --create-indexes

  # Clear existing data before import
  python import_data.py --provider SuperPharm --clear
        """
    )

    parser.add_argument(
        '--provider',
        help='Provider name to import (e.g., SuperPharm, Shufersal, Victory)',
        type=str
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Import all providers found in dumps folder'
    )
    parser.add_argument(
        '--implemented',
        action='store_true',
        help='Import only fully implemented parsers (SuperPharm, Shufersal, Victory)'
    )
    parser.add_argument(
        '--dumps',
        default='./dumps',
        help='Path to dumps folder (default: ./dumps)',
        type=str
    )
    parser.add_argument(
        '--database',
        default='supermarket_data',
        help='MongoDB database name (default: supermarket_data)',
        type=str
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing data for provider before importing'
    )
    parser.add_argument(
        '--create-indexes',
        action='store_true',
        help='Create MongoDB indexes for efficient querying'
    )
    parser.add_argument(
        '--list-parsers',
        action='store_true',
        help='List all available parsers (34 total)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics (document counts)'
    )

    args = parser.parse_args()

    # List parsers command
    if args.list_parsers:
        print("\n=== All Parsers (34 total) ===\n")
        print("Fully Implemented (P0):")
        for parser_name in ParserFactory.get_implemented_parsers():
            print(f"  ✅ {parser_name:20s} - Ready to import")

        print("\nSkeleton Parsers (P1 - To be implemented):")
        for parser_name in ParserFactory.get_skeleton_parsers():
            print(f"  ⏳ {parser_name:20s} - Not yet implemented")

        return 0

    # Stats command
    if args.stats:
        try:
            importer = MongoImporter(args.database)
            stats = importer.get_stats()
            print("\n=== Database Statistics ===")
            print(f"Database: {args.database}")
            print(f"Stores:     {stats['stores']:,}")
            print(f"Prices:     {stats['prices']:,}")
            print(f"Promotions: {stats['promotions']:,}")
            importer.close()
            return 0
        except Exception as e:
            print(f"Error getting stats: {e}", file=sys.stderr)
            return 1

    # Create indexes command
    if args.create_indexes:
        try:
            importer = MongoImporter(args.database)
            importer.create_indexes()
            importer.close()
            return 0
        except Exception as e:
            print(f"Error creating indexes: {e}", file=sys.stderr)
            return 1

    # Import commands
    try:
        runner = ImportRunner(dumps_folder=args.dumps, database_name=args.database)

        if args.implemented:
            print("\n=== Importing only fully implemented parsers ===")
            print("Parsers: SuperPharm, Shufersal, Victory\n")

            for provider in ParserFactory.get_implemented_parsers():
                try:
                    runner.import_provider(provider, clear_existing=args.clear)
                except Exception as e:
                    print(f"Error importing {provider}: {e}", file=sys.stderr)

            # Show final stats
            stats = runner.get_stats()
            print("\n=== Final Database Statistics ===")
            print(f"Total Stores:     {stats['stores']:,}")
            print(f"Total Prices:     {stats['prices']:,}")
            print(f"Total Promotions: {stats['promotions']:,}")

        elif args.all:
            print("\n=== Importing all providers ===\n")
            results = runner.import_all(implemented_only=False)

            # Show summary
            print("\n=== Import Summary ===")
            for provider, counts in results.items():
                print(f"{provider}:")
                print(f"  Stores: {counts['stores']}, Prices: {counts['prices']}, Promotions: {counts['promotions']}")

        elif args.provider:
            runner.import_provider(args.provider, clear_existing=args.clear)

            # Show stats
            stats = runner.get_stats()
            print("\n=== Database Statistics ===")
            print(f"Total Stores:     {stats['stores']:,}")
            print(f"Total Prices:     {stats['prices']:,}")
            print(f"Total Promotions: {stats['promotions']:,}")

        else:
            parser.print_help()
            return 1

        runner.close()
        return 0

    except NotImplementedError as e:
        print(f"\nError: {e}", file=sys.stderr)
        print("\nThis parser is not yet implemented. Use --list-parsers to see available parsers.", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
