CREATE ROLE STREAMLIT;
GRANT ROLE STREAMLIT TO USER STREAMLIT;
GRANT ROLE STREAMLIT TO ROLE SYSADMIN;

-- permissions
GRANT IMPORTED PRIVILEGES ON DATABASE CRUNCHBASE_BASIC_COMPANY_DATA TO ROLE STREAMLIT;
GRANT USAGE ON WAREHOUSE REPORTING_XS TO ROLE STREAMLIT;


--  countries DUMMY table
USE ROLE ACCOUNTADMIN;
-- create the database
CREATE DATABASE IF NOT EXISTS streamlit_db;

-- use the database
USE DATABASE streamlit_db;

-- create the table in the public schema
CREATE OR REPLACE TABLE public.countries (
  country_code VARCHAR(3),
  longitude FLOAT,
  latitude FLOAT,
  description VARCHAR(255)
);

GRANT IMPORTED PRIVILEGES ON DATABASE streamlit_db TO ROLE STREAMLIT;

-- insert data for GBR
INSERT INTO countries (country_code, longitude, latitude, description)
VALUES ('GBR', -0.1278, 51.5074, 'United Kingdom');

-- insert data for NLD
INSERT INTO countries (country_code, longitude, latitude, description)
VALUES ('NLD', 4.8970, 52.3779, 'Netherlands');

-- insert data for CAN
INSERT INTO countries (country_code, longitude, latitude, description)
VALUES ('CAN', -75.6972, 45.4215, 'Canada');

-- insert data for ZAF
INSERT INTO countries (country_code, longitude, latitude, description)
VALUES ('ZAF', 28.1871, -25.7460, 'South Africa');

-- insert data for FRA
INSERT INTO countries (country_code, longitude, latitude, description)
VALUES ('FRA', 2.3522, 48.8566, 'France');

-- insert data for MEX
INSERT INTO countries (country_code, longitude, latitude, description)
VALUES ('MEX', -99.1332, 19.4326, 'Mexico');

-- insert data for DNK
INSERT INTO countries (country_code, longitude, latitude, description)
VALUES ('DNK', 12.5683, 55.6761, 'Denmark');
