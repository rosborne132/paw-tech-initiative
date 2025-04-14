-- Clear tables
DROP TABLE IF EXISTS raw_data CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
DROP TABLE IF EXISTS animals CASCADE;
DROP TABLE IF EXISTS attributes CASCADE;
DROP TABLE IF EXISTS environment CASCADE;

-- Create ENUM types
DO $$ BEGIN
    CREATE TYPE age_enum AS ENUM ('kitten', 'adult', 'senior');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE species_enum AS ENUM ('dog', 'cat');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE size_enum AS ENUM ('small', 'medium', 'large');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE sex_enum AS ENUM ('male', 'female');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create storage table
CREATE TABLE raw_data (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,                    -- API source name
    raw_data JSONB NOT NULL,                        -- Store the raw API response as JSON
    fetched_at TIMESTAMPTZ DEFAULT NOW() NOT NULL   -- Timestamp of when the data was fetched
);

CREATE TABLE in_flight_data (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,                    -- API source name
    raw_data JSONB NOT NULL                         -- Store the raw API response as JSON
);

-- Create a function to handle the trigger
CREATE OR REPLACE FUNCTION insert_into_in_flight_data()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO in_flight_data (source, raw_data)
    VALUES (NEW.source, NEW.raw_data);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger on the raw_data table
CREATE TRIGGER after_insert_raw_data
AFTER INSERT ON raw_data
FOR EACH ROW
EXECUTE FUNCTION insert_into_in_flight_data();

-- Create Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    platform_organization_id VARCHAR(50) NULL DEFAULT NULL,
    name VARCHAR(255) NOT NULL DEFAULT NULL,
    city VARCHAR(255) NOT NULL DEFAULT NULL,
    state VARCHAR(2) NOT NULL DEFAULT NULL,
    posting_source VARCHAR(255) NOT NULL DEFAULT NULL
);

-- Create Animals table
CREATE TABLE IF NOT EXISTS animals (
    id SERIAL PRIMARY KEY,
    platform_animal_id VARCHAR(50) NULL DEFAULT NULL,
    name VARCHAR(255) NOT NULL DEFAULT NULL,
    age age_enum NULL DEFAULT NULL,
    species species_enum NOT NULL,
    breed VARCHAR(100) NOT NULL,
    sex sex_enum NOT NULL,
    size size_enum NULL DEFAULT NULL,
    description TEXT NULL DEFAULT NULL,
    adopted BOOLEAN NOT NULL,
    organization_id INTEGER REFERENCES organizations(id),
    posting_img_count SMALLINT NULL DEFAULT NULL,
    posting_source VARCHAR(255) NOT NULL,
    intake_date TIMESTAMPTZ NULL DEFAULT NULL,
    outcome_date TIMESTAMPTZ NULL DEFAULT NULL
);

-- Create Attributes table
CREATE TABLE IF NOT EXISTS attributes (
    id SERIAL PRIMARY KEY,
    animal_id BIGINT REFERENCES animals(id) ON DELETE CASCADE,
    spayed_neutered BOOLEAN NULL DEFAULT NULL,
    house_trained BOOLEAN NULL DEFAULT NULL,
    declawed BOOLEAN NULL DEFAULT NULL,
    special_needs BOOLEAN NULL DEFAULT NULL,
    shots_current BOOLEAN NULL DEFAULT NULL
);

-- Create Environment table
CREATE TABLE IF NOT EXISTS environment (
    id SERIAL PRIMARY KEY,
    animal_id BIGINT REFERENCES animals(id) ON DELETE CASCADE,
    dogs_ok BOOLEAN NULL DEFAULT NULL,
    cats_ok BOOLEAN NULL DEFAULT NULL,
    kids_ok BOOLEAN NULL DEFAULT NULL
);

-- Insert data into the organization table
INSERT INTO organizations (platform_organization_id, name, city, state, posting_source)
VALUES
    ('1', 'Sonoma Department of Health Services', 'Santa Rosa A', 'CA', 'data.sonomacounty.ca.gov'),
    ('2', 'Montgomery County Animal Services', 'Rockville', 'MD', 'catalog.data.gov'),
    ('3', 'City of Long Beach Animal Shelter', 'Long Beach', 'CA', 'data.longbeach.gov')
