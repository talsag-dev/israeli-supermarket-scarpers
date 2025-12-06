"""Victory XML parser."""
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List

from .base import AbstractParser


class VictoryParser(AbstractParser):
    """Parser for Victory XML format."""

    def __init__(self):
        """Initialize Victory parser."""
        super().__init__(provider_name="Victory")

    def parse_stores(self, xml_path: str) -> List[Dict]:
        """Parse Victory store XML.

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

        # Victory uses <Store Date="06/12/25" Time="06:00:01">
        # Format: DD/MM/YY HH:MM:SS
        date_attr = root.get('Date', '')
        time_attr = root.get('Time', '')

        update_datetime = None
        if date_attr and time_attr:
            try:
                update_datetime = datetime.strptime(f"{date_attr} {time_attr}", '%d/%m/%y %H:%M:%S')
            except ValueError:
                pass

        # Find all Branch elements
        for branch in root.findall('.//Branch'):
            last_update = self.safe_find_text(branch, 'LastUpdateDate')
            # Format: "25/07/2022 09:55:14"
            last_update_dt = self.safe_parse_date(last_update, ['%d/%m/%Y %H:%M:%S'])

            store = {
                'provider': self.provider_name,
                'chain_id': self.safe_find_text(branch, 'ChainID'),
                'chain_name': self.safe_find_text(branch, 'ChainName'),
                'sub_chain_id': self.safe_find_text(branch, 'SubChainID'),
                'sub_chain_name': self.safe_find_text(branch, 'SubChainName'),
                'store_id': self.safe_find_text(branch, 'StoreID'),
                'bikoret_no': self.safe_find_text(branch, 'BikoretNo'),
                'store_type': self.safe_find_text(branch, 'StoreType'),
                'store_name': self.safe_find_text(branch, 'StoreName'),
                'address': self.safe_find_text(branch, 'Address'),
                'city': self.safe_find_text(branch, 'City'),
                'zip_code': self.safe_find_text(branch, 'ZIPCode'),
                'last_updated': last_update_dt or update_datetime,
                'latitude': self.safe_find_text(branch, 'Latitude'),
                'longitude': self.safe_find_text(branch, 'Longitude'),
                'scraped_at': scraped_at,
            }
            stores.append(store)

        return stores

    def parse_prices(self, xml_path: str) -> List[Dict]:
        """Parse Victory price XML.

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

        chain_id = self.safe_find_text(root, 'ChainID')
        sub_chain_id = self.safe_find_text(root, 'SubChainID')
        store_id = self.safe_find_text(root, 'StoreID')
        bikoret_no = self.safe_find_text(root, 'BikoretNo')

        # Find all Product elements
        for product in root.findall('.//Product'):
            price_update_date = self.safe_find_text(product, 'PriceUpdateDate')
            # Victory format: "2018/08/07 07:17" or "YYYY/MM/DD HH:MM"
            date_obj = self.safe_parse_date(price_update_date, ['%Y/%m/%d %H:%M', '%Y/%m/%d'])

            last_update_date = self.safe_find_text(product, 'LastUpdateDate')
            last_update_time = self.safe_find_text(product, 'LastUpdateTime')
            last_update_dt = None
            if last_update_date and last_update_time:
                last_update_dt = self.safe_parse_date(
                    f"{last_update_date} {last_update_time}",
                    ['%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S']
                )

            price = {
                'provider': self.provider_name,
                'chain_id': chain_id,
                'sub_chain_id': sub_chain_id,
                'store_id': store_id,
                'bikoret_no': bikoret_no,
                'item_code': self.safe_find_text(product, 'ItemCode'),
                'item_type': self.safe_find_int(product, 'ItemType'),
                'item_name': self.safe_find_text(product, 'ItemName'),
                'manufacturer_name': self.safe_find_text(product, 'ManufactureName'),
                'manufacture_country': self.safe_find_text(product, 'ManufactureCountry'),
                'manufacturer_item_description': self.safe_find_text(product, 'ManufactureItemDescription'),
                'unit_qty': self.safe_find_text(product, 'UnitQty'),
                'quantity': self.safe_find_float(product, 'Quantity'),
                'unit_measure': self.safe_find_text(product, 'UnitMeasure'),
                'bis_weighted': self.safe_find_int(product, 'BisWeighted'),
                'qty_in_package': self.safe_find_float(product, 'QtyInPackage'),
                'item_price': self.safe_find_float(product, 'ItemPrice'),
                'unit_of_measure_price': self.safe_find_float(product, 'UnitOfMeasurePrice'),
                'allow_discount': self.safe_find_int(product, 'AllowDiscount'),
                'item_status': self.safe_find_int(product, 'itemStatus'),
                'price_update_date': date_obj,
                'last_update_date': last_update_dt,
                'scraped_at': scraped_at,
            }
            prices.append(price)

        return prices

    def parse_promotions(self, xml_path: str) -> List[Dict]:
        """Parse Victory promotion XML.

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

        chain_id = self.safe_find_text(root, 'ChainID')
        sub_chain_id = self.safe_find_text(root, 'SubChainID')
        store_id = self.safe_find_text(root, 'StoreID')
        bikoret_no = self.safe_find_text(root, 'BikoretNo')

        # Find all Sale elements
        for sale in root.findall('.//Sale'):
            price_update_date = self.safe_find_text(sale, 'PriceUpdateDate')
            promo_start_date = self.safe_find_text(sale, 'PromotionStartDate')
            promo_end_date = self.safe_find_text(sale, 'PromotionEndDate')

            # Parse dates - Victory format: "YYYY/MM/DD"
            update_date_obj = self.safe_parse_date(
                price_update_date,
                ['%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M', '%Y/%m/%d']
            )
            start_date_obj = self.safe_parse_date(promo_start_date, ['%Y/%m/%d'])
            end_date_obj = self.safe_parse_date(promo_end_date, ['%Y/%m/%d'])

            promotion = {
                'provider': self.provider_name,
                'chain_id': chain_id,
                'sub_chain_id': sub_chain_id,
                'store_id': store_id,
                'bikoret_no': bikoret_no,
                'item_code': self.safe_find_text(sale, 'ItemCode'),
                'item_type': self.safe_find_int(sale, 'ItemType'),
                'is_gift_item': self.safe_find_int(sale, 'IsGiftItem'),
                'reward_type': self.safe_find_int(sale, 'RewardType'),
                'allow_multiple_discounts': self.safe_find_int(sale, 'AllowMultipleDiscounts'),
                'promotion_id': self.safe_find_text(sale, 'PromotionID'),
                'promotion_description': self.safe_find_text(sale, 'PromotionDescription'),
                'promotion_start_date': start_date_obj,
                'promotion_start_hour': self.safe_find_text(sale, 'PromotionStartHour'),
                'promotion_end_date': end_date_obj,
                'promotion_end_hour': self.safe_find_text(sale, 'PromotionEndHour'),
                'club_id': self.safe_find_text(sale, 'ClubID'),
                'min_qty': self.safe_find_float(sale, 'MinQty'),
                'max_qty': self.safe_find_float(sale, 'MaxQty'),
                'discount_rate': self.safe_find_float(sale, 'DiscountRate'),
                'discount_type': self.safe_find_int(sale, 'DiscountType'),
                'min_purchase_amount': self.safe_find_float(sale, 'MinPurchaseAmount'),
                'discounted_price': self.safe_find_float(sale, 'DiscountedPrice'),
                'discounted_price_per_mida': self.safe_find_float(sale, 'DiscountedPricePerMida'),
                'min_no_of_items_offered': self.safe_find_int(sale, 'MinNoOfItemsOffered'),
                'additionals_coupon': self.safe_find_text(sale, 'AdditionalsCoupon'),
                'additionals_gift_count': self.safe_find_float(sale, 'AdditionalsGiftCount'),
                'additionals_totals': self.safe_find_text(sale, 'AdditionalsTotals'),
                'additionals_min_basket_amount': self.safe_find_float(sale, 'AdditionalsMinBasketAmount'),
                'additional_restrictions': self.safe_find_text(sale, 'AdditionalRestrictions'),
                'remarks': self.safe_find_text(sale, 'Remarks'),
                'price_update_date': update_date_obj,
                'scraped_at': scraped_at,
            }
            promotions.append(promotion)

        return promotions
