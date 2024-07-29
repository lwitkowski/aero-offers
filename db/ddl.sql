SET client_encoding = 'UTF8';

CREATE TABLE aircraft_offer (
    id SERIAL PRIMARY KEY,
    date DATE,
    creation_datetime TIMESTAMP WITH TIME ZONE,
    spider TEXT,
    price NUMERIC(15,2),
    currency TEXT,
    offer_url TEXT,
    location TEXT,
    title TEXT,
    hours INTEGER,
    starts INTEGER,
    detail_text text,
    aircraft_type TEXT,
    currency_code TEXT,
    manufacturer TEXT,
    model TEXT,
    classified BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE exchange_rates (
    currency TEXT PRIMARY KEY,
    rate NUMERIC(20, 10),
    last_update TIMESTAMP WITH TIME ZONE
);