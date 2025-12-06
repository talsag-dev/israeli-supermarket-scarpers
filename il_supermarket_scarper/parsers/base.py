"""Base parser for supermarket XML files."""
import os
import re
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional


class AbstractParser(ABC):
    """Base parser for supermarket XML files."""

    def __init__(self, provider_name: str) -> None:
        """Initialize parser with provider name.

        Args:
            provider_name: Name of the supermarket provider (e.g., "SuperPharm")
        """
        self.provider_name = provider_name

    @abstractmethod
    def parse_stores(self, xml_path: str) -> List[Dict]:
        """Parse store XML and return list of store dicts.

        Args:
            xml_path: Path to store XML file

        Returns:
            List of store dictionaries with standardized fields
        """

    @abstractmethod
    def parse_prices(self, xml_path: str) -> List[Dict]:
        """Parse price XML and return list of price dicts.

        Args:
            xml_path: Path to price XML file

        Returns:
            List of price dictionaries with standardized fields
        """

    @abstractmethod
    def parse_promotions(self, xml_path: str) -> List[Dict]:
        """Parse promo XML and return list of promo dicts.

        Args:
            xml_path: Path to promotion XML file

        Returns:
            List of promotion dictionaries with standardized fields
        """

    def extract_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract timestamp from filename: YYYYMMDDHHNN.

        Args:
            filename: XML filename (e.g., "Price7290172900007-057-202512061339.xml")

        Returns:
            datetime object if timestamp found, None otherwise
        """
        match = re.search(r'-(\d{12})\.xml$', filename)
        if match:
            timestamp_str = match.group(1)
            try:
                return datetime.strptime(timestamp_str, '%Y%m%d%H%M')
            except ValueError:
                return None
        return None

    def detect_file_type(self, filename: str) -> str:
        """Detect file type: stores, prices, promotions, or unknown.

        Args:
            filename: XML filename

        Returns:
            File type: 'stores', 'prices', 'promotions', or 'unknown'
        """
        filename_lower = filename.lower()
        if 'store' in filename_lower:
            return 'stores'
        elif 'price' in filename_lower:
            return 'prices'
        elif 'promo' in filename_lower:
            return 'promotions'
        return 'unknown'

    # Helper methods for safe XML extraction
    def safe_find_text(self, element: ET.Element, tag: str, default: str = '') -> str:
        """Safely extract text from XML element.

        Args:
            element: XML element to search within
            tag: Tag name to find
            default: Default value if tag not found or empty

        Returns:
            Text content or default value
        """
        found = element.find(tag)
        return found.text if found is not None and found.text else default

    def safe_find_float(self, element: ET.Element, tag: str, default: float = 0.0) -> float:
        """Safely extract float from XML element.

        Args:
            element: XML element to search within
            tag: Tag name to find
            default: Default value if tag not found or conversion fails

        Returns:
            Float value or default value
        """
        text = self.safe_find_text(element, tag, str(default))
        try:
            return float(text)
        except ValueError:
            return default

    def safe_find_int(self, element: ET.Element, tag: str, default: int = 0) -> int:
        """Safely extract int from XML element.

        Args:
            element: XML element to search within
            tag: Tag name to find
            default: Default value if tag not found or conversion fails

        Returns:
            Integer value or default value
        """
        text = self.safe_find_text(element, tag, str(default))
        try:
            return int(text)
        except ValueError:
            return default

    def safe_parse_date(self, date_str: str, formats: List[str]) -> Optional[datetime]:
        """Safely parse date string with multiple format attempts.

        Args:
            date_str: Date string to parse
            formats: List of date format strings to try (e.g., ['%Y-%m-%d', '%Y/%m/%d'])

        Returns:
            datetime object if parsing succeeds, None otherwise
        """
        if not date_str:
            return None

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
