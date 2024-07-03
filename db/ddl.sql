SET client_encoding = 'UTF8';

SET default_tablespace = '';
SET default_table_access_method = heap;

CREATE TABLE aircraft_offer (
    id integer NOT NULL,
    date date,
    creation_datetime timestamp without time zone,
    spider character varying,
    price numeric(15,2),
    currency character varying,
    offer_url character varying,
    location character varying,
    title character varying,
    hours integer,
    starts integer,
    detail_text text,
    aircraft_type character varying,
    currency_code character varying,
    manufacturer character varying,
    model character varying
);

CREATE SEQUENCE aircraft_offer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY aircraft_offer ALTER COLUMN id SET DEFAULT nextval('public.aircraft_offer_id_seq'::regclass);


CREATE TABLE exchange_rates (
    currency character varying NOT NULL,
    rate numeric(20,10),
    last_update timestamp without time zone
);

CREATE SEQUENCE feedback_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE feedback (
    id integer DEFAULT nextval('public.feedback_id_seq'::regclass) NOT NULL,
    creation_datetime timestamp without time zone,
    email character varying,
    message character varying
);

ALTER TABLE ONLY aircraft_offer
    ADD CONSTRAINT aircraft_offer_pkey PRIMARY KEY (id);
ALTER TABLE ONLY exchange_rates
    ADD CONSTRAINT exchange_rates_pkey PRIMARY KEY (currency);
ALTER TABLE ONLY feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);