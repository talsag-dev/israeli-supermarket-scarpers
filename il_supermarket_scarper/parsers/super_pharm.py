"""SuperPharm XML parser."""
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List

from .base import AbstractParser


class SuperPharmParser(AbstractParser):
    """Parser for SuperPharm XML format."""

    def __init__(self):
        """Initialize SuperPharm parser."""
        super().__init__(provider_name="SuperPharm")

    def parse_stores(self, xml_path: str) -> List[Dict]:
        """Parse SuperPharm store XML.

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

        chain_id = self.safe_find_text(root, 'ChainId')
        chain_name = self.safe_find_text(root, 'ChainName')
        last_update_date = self.safe_find_text(root, 'LastUpdateDate')

        # Parse date
        date_obj = self.safe_parse_date(last_update_date, ['%Y-%m-%d'])

        # Find all SubChains → Stores → Store
        for subchain in root.findall('.//SubChain'):
            sub_chain_id = self.safe_find_text(subchain, 'SubChainID')

            for store_elem in subchain.findall('.//Store'):
                store = {
                    'provider': self.provider_name,
                    'chain_id': chain_id,
                    'chain_name': chain_name,
                    'sub_chain_id': sub_chain_id,
                    'store_id': self.safe_find_text(store_elem, 'StoreID'),
                    'bikoret_no': self.safe_find_text(store_elem, 'BikoretNo'),
                    'store_type': self.safe_find_text(store_elem, 'StoreType'),
                    'store_name': self.safe_find_text(store_elem, 'StoreName'),
                    'address': self.safe_find_text(store_elem, 'Address'),
                    'city': self.safe_find_text(store_elem, 'City'),
                    'zip_code': self.safe_find_text(store_elem, 'ZipCode'),
                    'last_updated': date_obj,
                    'scraped_at': scraped_at,
                }
                stores.append(store)

        return stores

    def parse_prices(self, xml_path: str) -> List[Dict]:
        """Parse SuperPharm price XML.

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

        # Extract envelope data
        envelope = root.find('Envelope')
        if envelope is None:
            return prices

        chain_id = self.safe_find_text(envelope, 'ChainId')
        sub_chain_id = self.safe_find_text(envelope, 'SubChainId')
        store_id = self.safe_find_text(envelope, 'StoreId')
        bikoret_no = self.safe_find_text(envelope, 'BikoretNo')

        # Find all Line elements
        for line in envelope.findall('.//Line'):
            price_update_date = self.safe_find_text(line, 'PriceUpdateDate')
            date_obj = self.safe_parse_date(price_update_date, ['%Y-%m-%d'])

            price = {
                'provider': self.provider_name,
                'chain_id': chain_id,
                'sub_chain_id': sub_chain_id,
                'store_id': store_id,
                'bikoret_no': bikoret_no,
                'item_code': self.safe_find_text(line, 'ItemCode'),
                'item_name': self.safe_find_text(line, 'ItemName'),
                'manufacturer_name': self.safe_find_text(line, 'ManufacturerName'),
                'manufacture_country': self.safe_find_text(line, 'ManufactureCountry'),
                'manufacturer_item_description': self.safe_find_text(line, 'ManufacturerItemDescription'),
                'unit_qty': self.safe_find_text(line, 'UnitQty'),
                'quantity': self.safe_find_float(line, 'Quantity'),
                'unit_of_measure': self.safe_find_float(line, 'UnitOfMeasure'),
                'bls_weighted': self.safe_find_int(line, 'blsWeighted'),
                'qty_in_package': self.safe_find_float(line, 'QtyInPackage'),
                'item_price': self.safe_find_float(line, 'ItemPrice'),
                'unit_of_measure_price': self.safe_find_float(line, 'UnitOfMeasurePrice'),
                'allow_discount': self.safe_find_int(line, 'AllowDiscount'),
                'item_status': self.safe_find_int(line, 'ItemStatus'),
                'price_update_date': date_obj,
                'scraped_at': scraped_at,
            }
            prices.append(price)

        return prices

    def parse_promotions(self, xml_path: str) -> List[Dict]:
        """Parse SuperPharm promotion XML.

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

        # Extract envelope data
        envelope = root.find('Envelope')
        if envelope is None:
            return promotions

        chain_id = self.safe_find_text(envelope, 'ChainId')
        sub_chain_id = self.safe_find_text(envelope, 'SubChainId')
        store_id = self.safe_find_text(envelope, 'StoreId')
        bikoret_no = self.safe_find_text(envelope, 'BikoretNo')

        # Find all Line elements
        for line in envelope.findall('.//Line'):
            price_update_date = self.safe_find_text(line, 'PriceUpdateDate')
            date_obj = self.safe_parse_date(price_update_date, ['%Y-%m-%d %H:%M:%S'])

            promo_details = line.find('PromotionDetails')
            if promo_details is None:
                continue

            promo_start_date = self.safe_find_text(promo_details, 'PromotionStartDate')
            promo_end_date = self.safe_find_text(promo_details, 'PromotionEndDate')

            promotion = {
                'provider': self.provider_name,
                'chain_id': chain_id,
                'sub_chain_id': sub_chain_id,
                'store_id': store_id,
                'bikoret_no': bikoret_no,
                'item_code': self.safe_find_text(line, 'ItemCode'),
                'is_gift_item': self.safe_find_int(line, 'IsGiftItem'),
                'reward_type': self.safe_find_int(line, 'RewardType'),
                'allow_multiple_discounts': self.safe_find_int(line, 'AllowMultipleDiscounts'),
                'promotion_id': self.safe_find_text(line, 'PromotionId'),
                'promotion_description': self.safe_find_text(promo_details, 'PromotionDescription'),
                'promotion_start_date': self.safe_parse_date(promo_start_date, ['%Y-%m-%d']),
                'promotion_end_date': self.safe_parse_date(promo_end_date, ['%Y-%m-%d']),
                'promotion_start_hour': self.safe_find_text(promo_details, 'PromotionStartHour'),
                'promotion_end_hour': self.safe_find_text(promo_details, 'PromotionEndHour'),
                'club_id': self.safe_find_text(promo_details, 'ClubId'),
                'min_qty': self.safe_find_float(promo_details, 'MinQty'),
                'max_qty': self.safe_find_float(promo_details, 'MaxQty'),
                'discount_rate': self.safe_find_float(promo_details, 'DiscountRate'),
                'discount_type': self.safe_find_int(promo_details, 'DiscountType'),
                'min_purchase_amnt': self.safe_find_float(promo_details, 'MinPurchaseAmnt'),
                'discounted_price': self.safe_find_float(promo_details, 'DiscountedPrice'),
                'discounted_price_per_mida': self.safe_find_float(promo_details, 'DiscountedPricePerMida'),
                'min_no_of_item_offered': self.safe_find_int(promo_details, 'MinNoOfItemOfered'),
                'additional_is_coupon': self.safe_find_int(promo_details, 'AdditionalIsCoupon'),
                'additional_gift_count': self.safe_find_float(promo_details, 'AdditionalGiftCount'),
                'additional_is_total': self.safe_find_int(promo_details, 'AdditionalIsTotal'),
                'additional_min_basket_amount': self.safe_find_float(promo_details, 'AdditionalMinBasketAmount'),
                'remarks': self.safe_find_text(promo_details, 'Remarks'),
                'price_update_date': date_obj,
                'scraped_at': scraped_at,
            }
            promotions.append(promotion)

        return promotions
