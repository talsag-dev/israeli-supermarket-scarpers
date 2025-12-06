"""Parser factory for mapping all 34 scrapers to parsers."""
from enum import Enum
from pathlib import Path
from typing import Optional

from .parsers.base import AbstractParser

# Import all 34 parsers
from .parsers.super_pharm import SuperPharmParser
from .parsers.shufersal import ShufersalParser
from .parsers.victory import VictoryParser
from .parsers.bareket import BareketParser
from .parsers.bitan import BitanParser
from .parsers.city_market import CityMarketParser
from .parsers.cofix import CofixParser
from .parsers.doralon import DoralonParser
from .parsers.good_pharm import GoodPharmParser
from .parsers.hazihinam import HazihinamParser
from .parsers.het_cohen import HetCohenParser
from .parsers.keshet import KeshetParser
from .parsers.king_store import KingStoreParser
from .parsers.maayan2000 import Maayan2000Parser
from .parsers.machsani_ashuk import MachsaniAshukParser
from .parsers.mega import MegaParser
from .parsers.meshnat_yosef import MeshnatYosefParser
from .parsers.nativ_hashed import NativHashedParser
from .parsers.osherad import OsheradParser
from .parsers.polizer import PolizerParser
from .parsers.quik import QuikParser
from .parsers.ramilevy import RamiLevyParser
from .parsers.salachdabach import SalachDabachParser
from .parsers.shefa_barcart_ashem import ShefaBarcartAshemParser
from .parsers.shuk_ahir import ShukAhirParser
from .parsers.stop_market import StopMarketParser
from .parsers.super_sapir import SuperSapirParser
from .parsers.super_yuda import SuperYudaParser
from .parsers.superdosh import SuperdoshParser
from .parsers.tivtaam import TivtaamParser
from .parsers.wolt import WoltParser
from .parsers.yellow import YellowParser
from .parsers.yohananof import YohananofParser
from .parsers.zolvebegadol import ZolvebegadolParser


class ParserFactory(Enum):
    """Factory mapping all 34 scrapers to parsers."""

    # P0 - Fully implemented
    SUPER_PHARM = SuperPharmParser
    SUPERPHARM = SuperPharmParser  # Alias
    SHUFERSAL = ShufersalParser
    VICTORY = VictoryParser

    # P1 - Skeleton parsers (to be implemented)
    BAREKET = BareketParser
    BITAN = BitanParser
    CITY_MARKET = CityMarketParser
    CITYMARKET = CityMarketParser  # Alias
    COFIX = CofixParser
    DORALON = DoralonParser
    GOOD_PHARM = GoodPharmParser
    GOODPHARM = GoodPharmParser  # Alias
    HAZIHINAM = HazihinamParser
    HET_COHEN = HetCohenParser
    HETCOHEN = HetCohenParser  # Alias
    KESHET = KeshetParser
    KING_STORE = KingStoreParser
    KINGSTORE = KingStoreParser  # Alias
    MAAYAN2000 = Maayan2000Parser
    MACHSANI_ASHUK = MachsaniAshukParser
    MACHSANIASHUK = MachsaniAshukParser  # Alias
    MEGA = MegaParser
    MESHNAT_YOSEF = MeshnatYosefParser
    MESHNATYOSEF = MeshnatYosefParser  # Alias
    NATIV_HASHED = NativHashedParser
    NATIVHASHED = NativHashedParser  # Alias
    OSHERAD = OsheradParser
    POLIZER = PolizerParser
    QUIK = QuikParser
    RAMILEVY = RamiLevyParser
    RAMI_LEVY = RamiLevyParser  # Alias
    SALACHDABACH = SalachDabachParser
    SHEFA_BARCART_ASHEM = ShefaBarcartAshemParser
    SHUK_AHIR = ShukAhirParser
    SHUKAHIR = ShukAhirParser  # Alias
    STOP_MARKET = StopMarketParser
    STOPMARKET = StopMarketParser  # Alias
    SUPER_SAPIR = SuperSapirParser
    SUPERSAPIR = SuperSapirParser  # Alias
    SUPER_YUDA = SuperYudaParser
    SUPERYUDA = SuperYudaParser  # Alias
    SUPERDOSH = SuperdoshParser
    TIVTAAM = TivtaamParser
    WOLT = WoltParser
    YELLOW = YellowParser
    YOHANANOF = YohananofParser
    ZOLVEBEGADOL = ZolvebegadolParser

    @classmethod
    def get_parser(cls, provider_name: str) -> Optional[AbstractParser]:
        """Get parser instance by provider name.

        Args:
            provider_name: Name of the provider (e.g., "SuperPharm")

        Returns:
            Parser instance or None if not found
        """
        # Normalize provider name: uppercase, replace spaces and hyphens with underscore
        provider_key = provider_name.upper().replace(' ', '_').replace('-', '_')

        try:
            parser_class = cls[provider_key].value
            return parser_class()
        except KeyError:
            return None

    @classmethod
    def detect_provider_from_path(cls, file_path: str) -> Optional[str]:
        """Extract provider from path: dumps/SuperPharm/... → SuperPharm.

        Args:
            file_path: Path to XML file

        Returns:
            Provider name or None if not found
        """
        path_parts = Path(file_path).parts
        if 'dumps' in path_parts:
            dumps_index = path_parts.index('dumps')
            if len(path_parts) > dumps_index + 1:
                return path_parts[dumps_index + 1]
        return None

    @classmethod
    def all_parsers(cls) -> list:
        """Return list of all unique parser names.

        Returns:
            List of parser names
        """
        seen = set()
        result = []
        for member in cls:
            if member.value not in seen:
                seen.add(member.value)
                # Get clean name without underscores
                clean_name = member.name.replace('_', '')
                result.append(clean_name)
        return sorted(result)

    @classmethod
    def has_parser(cls, provider_name: str) -> bool:
        """Check if parser exists for provider.

        Args:
            provider_name: Name of the provider

        Returns:
            True if parser exists, False otherwise
        """
        return cls.get_parser(provider_name) is not None

    @classmethod
    def get_implemented_parsers(cls) -> list:
        """Return list of fully implemented parsers (not skeletons).

        Returns:
            List of implemented parser names
        """
        # TODO: Update this list as more parsers are implemented
        return ['SuperPharm', 'Shufersal', 'Victory']

    @classmethod
    def get_skeleton_parsers(cls) -> list:
        """Return list of skeleton parsers (not yet implemented).

        Returns:
            List of skeleton parser names
        """
        all_parsers = set(cls.all_parsers())
        implemented = set(cls.get_implemented_parsers())
        skeletons = all_parsers - implemented
        return sorted(list(skeletons))
