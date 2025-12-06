"""Superdosh parser XML parser - TODO: Implement."""
from typing import Dict, List

from .base import AbstractParser


class SuperdoshParser(AbstractParser):
    """Parser for Superdosh XML format - TODO: Implement."""

    def __init__(self):
        """Initialize Superdosh parser."""
        super().__init__(provider_name="Superdosh")

    def parse_stores(self, xml_path: str) -> List[Dict]:
        """TODO: Implement Superdosh store parsing.

        Args:
            xml_path: Path to store XML file

        Returns:
            List of store dictionaries

        Raises:
            NotImplementedError: This parser is not yet implemented
        """
        raise NotImplementedError(f"{self.provider_name} store parsing not yet implemented")

    def parse_prices(self, xml_path: str) -> List[Dict]:
        """TODO: Implement Superdosh price parsing.

        Args:
            xml_path: Path to price XML file

        Returns:
            List of price dictionaries

        Raises:
            NotImplementedError: This parser is not yet implemented
        """
        raise NotImplementedError(f"{self.provider_name} price parsing not yet implemented")

    def parse_promotions(self, xml_path: str) -> List[Dict]:
        """TODO: Implement Superdosh promotion parsing.

        Args:
            xml_path: Path to promotion XML file

        Returns:
            List of promotion dictionaries

        Raises:
            NotImplementedError: This parser is not yet implemented
        """
        raise NotImplementedError(f"{self.provider_name} promotion parsing not yet implemented")
