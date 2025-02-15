from dataclasses import dataclass
from datetime import date
from enum import Enum

class AircraftCategory(Enum):
    glider = 1
    airplane = 2
    tmg = 3
    ultralight = 4
    helicopter = 5
    unknown = 99


@dataclass
class OfferPageItem:
    url: str
    category: AircraftCategory
    title: str
    published_at: date
    page_content: str

    # parsed content
    location: str = None  # address, like Hamburg, Germany
    hours: int = None
    starts: int = None

    raw_price: str = None  # e.g "123.00 $"
    price: str = None  # e.g "123.00"
    currency: str = None  # e.g USD
    price_in_euro: str = None
    exchange_rate: float = None  # e.g. 1.0

