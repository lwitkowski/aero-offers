import hashlib
from dataclasses import dataclass
from datetime import date
from enum import auto, StrEnum


class AircraftCategory(StrEnum):
    glider = auto()
    airplane = auto()
    tmg = auto()
    ultralight = auto()
    helicopter = auto()
    unknown = auto()


@dataclass
class OfferPageItem:
    url: str
    category: AircraftCategory
    title: str
    published_at: date
    page_content: str

    # parsed content
    location: str | None = None  # address, like Hamburg, Germany
    hours: int | None = None
    starts: int | None = None

    raw_price: str | None = None  # e.g "123.00 $"
    price: str | None = None  # e.g "123.00"
    currency: str | None = None  # e.g USD
    price_in_euro: str | None = None
    exchange_rate: float | None = None  # e.g. 1.0


@dataclass
class OfferPrice:
    amount: str
    currency: str
    amount_in_euro: str
    exchange_rate: float


@dataclass
class Offer:
    url: str
    category: str
    title: str
    published_at: date
    location: str
    hours: int
    starts: int
    price: OfferPrice
    manufacturer: str
    model: str
    spider: str | None


@dataclass(frozen=True)
class UnclassifiedOffer:
    id: str
    title: str
    category: AircraftCategory


def url_to_id(url: str) -> str:
    """Generate a deterministic ID from a URL using SHA-256 hash."""
    return hashlib.sha256(url.encode()).hexdigest()
