import datetime

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.types import Date, DateTime, Unicode, Numeric, Integer

from my_logging import *
from settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PW

logger = logging.getLogger('db')

Base = declarative_base()

class AircraftOffer(Base):
    __tablename__ = "aircraft_offer"

    id = Column('id', Integer, primary_key=True)
    date = Column(Date)
    creation_datetime = Column(DateTime)
    spider = Column(Unicode)
    price = Column(Numeric(precision=15, scale=2))
    currency = Column(Unicode)
    currency_code = Column(Unicode)
    offer_url = Column(Unicode)
    location = Column(Unicode)
    title = Column(Unicode)
    hours = Column(Integer)
    starts = Column(Integer)
    detail_text = Column(Text)
    aircraft_type = Column(Unicode)

    manufacturer = Column(Unicode)
    model = Column(Unicode)

    classified = Column(Boolean, default=False)

    def as_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d"),
            "creationDate": self.creation_datetime,
            "url": self.offer_url,
            "title": self.title,
            "price": self.price,
            "currency": self.currency,
            "currency_code": self.currency_code,
            "location": self.location,
            "aircraft_type": self.aircraft_type,
            "manufacturer": self.manufacturer,
            "model": self.model
        }

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    currency = Column(Unicode, primary_key=True)
    rate = Column(Numeric(precision=20, scale=10))  # TODO verify how much precision is necessary
    last_update = Column(DateTime)


logger.info('DB: postgresql+psycopg2://{0}:***@{1}:{2}/{3}'.format(DB_USER, DB_HOST, DB_PORT, DB_NAME))
engine = create_engine('postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, DB_PW, DB_HOST, DB_PORT, DB_NAME))
Session = sessionmaker(bind=engine)

def truncate_offers():
    session = Session()
    session.execute(text("TRUNCATE aircraft_offer"))
    session.commit()
    session.close()

def store_entity(entity):
    session = Session()
    session.add(entity)
    session.commit()
    session.close()


def store_offer(aircraft_offer):
    # TODO check instance type if aircraft_offer here
    logger.debug("Starting new database session")
    store_entity(aircraft_offer)


def update_exchange_rate(exchange_rate):
    session = Session()
    exchange_rate.last_update = datetime.datetime.now()
    session.merge(exchange_rate)
    session.commit()


def offer_url_exists(offer_url):
    session = Session()
    try:
        q = session.query(AircraftOffer).where(AircraftOffer.offer_url == offer_url).exists()
        result = session.query(q).one()
        return result is not None and result[0]
    except Exception as e:
        logger.error(e)
        logger.error("database error, assuming we don't have this offer already")
        return False
    finally:
        session.close()

def get_exchange_rates_as_dict(session):
    all_exchange_rates = session.query(ExchangeRate).all()
    exchange_rates = dict()
    for rate in all_exchange_rates:
        exchange_rates[rate.currency] = rate.rate
    return exchange_rates


def convert_prices(offers, session):
    exchange_rates = get_exchange_rates_as_dict(session)
    for offer in offers:
        offer["price_in_euro"] = offer["price"]
        offer["exchange_rate"] = "1.0"

        if offer["currency_code"] and offer["currency_code"] != "EUR":
            # EZB exchange rates are base=EUR, quote=X
            offer["price_in_euro"] = round(offer["price"] / exchange_rates[offer["currency_code"]], 2)
            offer["exchange_rate"] = exchange_rates[offer["currency_code"]]
    return offers


def get_offers_for_model(manufacturer, model):
    session = Session()
    try:
        offers = session.query(AircraftOffer)
        offers = offers.filter(AircraftOffer.manufacturer == manufacturer)
        offers = offers.filter(AircraftOffer.model == model)
        offers = offers.order_by(AircraftOffer.date.asc())
        offers = offers.all()

        ret = [offer.as_dict() for offer in offers]
        ret = convert_prices(ret, session)
        return ret
    finally:
        session.close()


def get_offers_dict(limit: int = 30, offset: int = 0, aircraft_type=None):
    session = Session()
    try:
        offers = session.query(AircraftOffer).order_by(AircraftOffer.date.desc())
        if aircraft_type is not None:
            offers = offers.filter(AircraftOffer.aircraft_type == aircraft_type)
        else:
            offers = offers.filter(AircraftOffer.aircraft_type is not None)

        offers = offers.limit(min(limit, 100))

        if offset is not None:
            offers = offers.offset(offset)
        offers = offers.all()

        ret = [offer.as_dict() for offer in offers]
        ret = convert_prices(ret, session)
        return ret
    finally:
        session.close()
