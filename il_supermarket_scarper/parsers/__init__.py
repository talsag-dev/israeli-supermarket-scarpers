"""XML parsers for all 34 supermarket chains."""
from .base import AbstractParser

# P0 - Fully implemented
from .super_pharm import SuperPharmParser
from .shufersal import ShufersalParser
from .victory import VictoryParser

# P1 - Skeletons (import all 31)
from .bareket import BareketParser
from .bitan import BitanParser
from .city_market import CityMarketParser
from .cofix import CofixParser
from .doralon import DoralonParser
from .good_pharm import GoodPharmParser
from .hazihinam import HazihinamParser
from .het_cohen import HetCohenParser
from .keshet import KeshetParser
from .king_store import KingStoreParser
from .maayan2000 import Maayan2000Parser
from .machsani_ashuk import MachsaniAshukParser
from .mega import MegaParser
from .meshnat_yosef import MeshnatYosefParser
from .nativ_hashed import NativHashedParser
from .osherad import OsheradParser
from .polizer import PolizerParser
from .quik import QuikParser
from .ramilevy import RamiLevyParser
from .salachdabach import SalachDabachParser
from .shefa_barcart_ashem import ShefaBarcartAshemParser
from .shuk_ahir import ShukAhirParser
from .stop_market import StopMarketParser
from .super_sapir import SuperSapirParser
from .super_yuda import SuperYudaParser
from .superdosh import SuperdoshParser
from .tivtaam import TivtaamParser
from .wolt import WoltParser
from .yellow import YellowParser
from .yohananof import YohananofParser
from .zolvebegadol import ZolvebegadolParser

__all__ = [
    'AbstractParser',
    # P0
    'SuperPharmParser',
    'ShufersalParser',
    'VictoryParser',
    # P1
    'BareketParser',
    'BitanParser',
    'CityMarketParser',
    'CofixParser',
    'DoralonParser',
    'GoodPharmParser',
    'HazihinamParser',
    'HetCohenParser',
    'KeshetParser',
    'KingStoreParser',
    'Maayan2000Parser',
    'MachsaniAshukParser',
    'MegaParser',
    'MeshnatYosefParser',
    'NativHashedParser',
    'OsheradParser',
    'PolizerParser',
    'QuikParser',
    'RamiLevyParser',
    'SalachDabachParser',
    'ShefaBarcartAshemParser',
    'ShukAhirParser',
    'StopMarketParser',
    'SuperSapirParser',
    'SuperYudaParser',
    'SuperdoshParser',
    'TivtaamParser',
    'WoltParser',
    'YellowParser',
    'YohananofParser',
    'ZolvebegadolParser',
]
