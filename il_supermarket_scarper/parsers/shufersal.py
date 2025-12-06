"""Shufersal XML parser."""
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List

from .base import AbstractParser


class ShufersalParser(AbstractParser):
    """Parser for Shufersal XML format."""

    def __init__(self):
        """Initialize Shufersal parser."""
        super().__init__(provider_name="Shufersal")

    def parse_stores(self, xml_path: str) -> List[Dict]:
        """Parse Shufersal store XML (SAP asx:abap format).

        Args:
            xml_path: Path to store XML file

        Returns:
            List of store dictionaries
        """
        stores = []
        filename = os.path.basename(xml_path)
        scraped_at = self.extract_timestamp_from_filename(filename)

        tree = ET.parse(xml_path)
        root = tree.getroot()

        # SAP format: all elements concatenated without proper nesting
        # Extract CHAINID
        chain_id_elem = root.find('.//{http://www.sap.com/abapxml}values/CHAINID')
        chain_id = chain_id_elem.text if chain_id_elem is not None and chain_id_elem.text else ''

        # Find all STORE elements
        stores_container = root.find('.//{http://www.sap.com/abapxml}values/STORES')
        if stores_container is None:
            return stores

        for store_elem in stores_container.findall('STORE'):
            store = {
                'provider': self.provider_name,
                'chain_id': chain_id,
                'chain_name': self.safe_find_text(store_elem, 'CHAINNAME'),
                'sub_chain_id': self.safe_find_text(store_elem, 'SUBCHAINID'),
                'store_id': self.safe_find_text(store_elem, 'STOREID'),
                'bikoret_no': self.safe_find_text(store_elem, 'BIKORETNO'),
                'store_type': self.safe_find_text(store_elem, 'STORETYPE'),
                'sub_chain_name': self.safe_find_text(store_elem, 'SUBCHAINNAME'),
                'store_name': self.safe_find_text(store_elem, 'STORENAME'),
                'address': self.safe_find_text(store_elem, 'ADDRESS'),
                'city': self.safe_find_text(store_elem, 'CITY'),
                'zip_code': self.safe_find_text(store_elem, 'ZIPCODE'),
                'scraped_at': scraped_at,
            }
            stores.append(store)

        return stores

    def parse_prices(self, xml_path: str) -> List[Dict]:
        """Parse Shufersal price XML.

        Args:
            xml_path: Path to price XML file

        Returns:
            List of price dictionaries
        """
        prices = []
        filename = os.path.basename(xml_path)
        scraped_at = self.extract_timestamp_from_filename(filename)

        tree = ET.parse(xml_path)
        root = tree.getroot()

        chain_id = self.safe_find_text(root, 'ChainId')
        sub_chain_id = self.safe_find_text(root, 'SubChainId')
        store_id = self.safe_find_text(root, 'StoreId')
        bikoret_no = self.safe_find_text(root, 'BikoretNo')

        # Find all Item elements
        for item in root.findall('.//Item'):
            price_update_date = self.safe_find_text(item, 'PriceUpdateDate')
            # Format: "2025-12-06 00:55"
            date_obj = self.safe_parse_date(price_update_date, ['%Y-%m-%d %H:%M'])

            price = {
                'provider': self.provider_name,
                'chain_id': chain_id,
                'sub_chain_id': sub_chain_id,
                'store_id': store_id,
                'bikoret_no': bikoret_no,
                'item_code': self.safe_find_text(item, 'ItemCode'),
                'item_type': self.safe_find_int(item, 'ItemType'),
                'item_name': self.safe_find_text(item, 'ItemName'),
                'manufacturer_name': self.safe_find_text(item, 'ManufacturerName'),
                'manufacture_country': self.safe_find_text(item, 'ManufactureCountry'),
                'manufacturer_item_description': self.safe_find_text(item, 'ManufacturerItemDescription'),
                'unit_qty': self.safe_find_text(item, 'UnitQty'),
                'quantity': self.safe_find_float(item, 'Quantity'),
                'b_is_weighted': self.safe_find_int(item, 'bIsWeighted'),
                'unit_of_measure': self.safe_find_text(item, 'UnitOfMeasure'),
                'qty_in_package': self.safe_find_float(item, 'QtyInPackage'),
                'item_price': self.safe_find_float(item, 'ItemPrice'),
                'unit_of_measure_price': self.safe_find_float(item, 'UnitOfMeasurePrice'),
                'allow_discount': self.safe_find_int(item, 'AllowDiscount'),
                'item_status': self.safe_find_int(item, 'ItemStatus'),
                'price_update_date': date_obj,
                'scraped_at': scraped_at,
            }
            prices.append(price)

        return prices

    def parse_promotions(self, xml_path: str) -> List[Dict]:
        """Parse Shufersal promotion XML.

        Args:
            xml_path: Path to promotion XML file

        Returns:
            List of promotion dictionaries
        """
        promotions = []
        filename = os.path.basename(xml_path)
        scraped_at = self.extract_timestamp_from_filename(filename)

        tree = ET.parse(xml_path)
        root = tree.getroot()

        chain_id = self.safe_find_text(root, 'ChainId')
        sub_chain_id = self.safe_find_text(root, 'SubChainId')
        store_id = self.safe_find_text(root, 'StoreId')
        bikoret_no = self.safe_find_text(root, 'BikoretNo')

        # Find all Promotion elements
        for promo in root.findall('.//Promotion'):
            promo_update_date = self.safe_find_text(promo, 'PromotionUpdateDate')
            promo_start_date = self.safe_find_text(promo, 'PromotionStartDate')
            promo_end_date = self.safe_find_text(promo, 'PromotionEndDate')

            # Parse dates
            update_date_obj = self.safe_parse_date(promo_update_date, ['%Y-%m-%d %H:%M'])
            start_date_obj = self.safe_parse_date(promo_start_date, ['%Y-%m-%d'])
            end_date_obj = self.safe_parse_date(promo_end_date, ['%Y-%m-%d'])

            # Extract promotion items
            promo_items = []
            promo_items_container = promo.find('PromotionItems')
            if promo_items_container is not None:
                for item in promo_items_container.findall('Item'):
                    promo_items.append({
                        'item_code': self.safe_find_text(item, 'ItemCode'),
                        'item_type': self.safe_find_int(item, 'ItemType'),
                        'is_gift_item': self.safe_find_int(item, 'IsGiftItem'),
                    })

            # Extract additional restrictions
            additional_restrictions = promo.find('AdditionalRestrictions')
            additional_is_coupon = 0
            additional_gift_count = 0
            additional_is_total = 0
            additional_is_active = 0
            if additional_restrictions is not None:
                additional_is_coupon = self.safe_find_int(additional_restrictions, 'AdditionalIsCoupon')
                additional_gift_count = self.safe_find_int(additional_restrictions, 'AdditionalGiftCount')
                additional_is_total = self.safe_find_int(additional_restrictions, 'AdditionalIsTotal')
                additional_is_active = self.safe_find_int(additional_restrictions, 'AdditionalIsActive')

            # Extract club IDs
            club_ids = []
            clubs_container = promo.find('Clubs')
            if clubs_container is not None:
                for club_elem in clubs_container.findall('ClubId'):
                    if club_elem.text:
                        club_ids.append(club_elem.text)

            promotion = {
                'provider': self.provider_name,
                'chain_id': chain_id,
                'sub_chain_id': sub_chain_id,
                'store_id': store_id,
                'bikoret_no': bikoret_no,
                'promotion_id': self.safe_find_text(promo, 'PromotionId'),
                'allow_multiple_discounts': self.safe_find_int(promo, 'AllowMultipleDiscounts'),
                'promotion_description': self.safe_find_text(promo, 'PromotionDescription'),
                'promotion_update_date': update_date_obj,
                'promotion_start_date': start_date_obj,
                'promotion_start_hour': self.safe_find_text(promo, 'PromotionStartHour'),
                'promotion_end_date': end_date_obj,
                'promotion_end_hour': self.safe_find_text(promo, 'PromotionEndHour'),
                'is_weighted_promo': self.safe_find_int(promo, 'IsWeightedPromo'),
                'min_qty': self.safe_find_float(promo, 'MinQty'),
                'reward_type': self.safe_find_int(promo, 'RewardType'),
                'discounted_price': self.safe_find_float(promo, 'DiscountedPrice'),
                'min_no_of_item_offered': self.safe_find_int(promo, 'MinNoOfItemOfered'),
                'promotion_items': promo_items,
                'additional_is_coupon': additional_is_coupon,
                'additional_gift_count': additional_gift_count,
                'additional_is_total': additional_is_total,
                'additional_is_active': additional_is_active,
                'club_ids': club_ids,
                'scraped_at': scraped_at,
            }
            promotions.append(promotion)

        return promotions
