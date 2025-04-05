-- Clear tables
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
    source VARCHAR(50) NOT NULL, -- API source name
    raw_data JSONB NOT NULL,     -- Store the raw API response as JSON
    fetched_at TIMESTAMPTZ
);

-- Create Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL
);

-- Create Animals table
CREATE TABLE IF NOT EXISTS animals (
    id SERIAL PRIMARY KEY,
    platform_animal_id VARCHAR(25) NOT NULL,
    name VARCHAR(255) NOT NULL,
    age age_enum NULL,
    species species_enum NOT NULL,
    breed VARCHAR(100) UNIQUE,
    sex sex_enum NOT NULL,
    size size_enum NULL,
    description TEXT NULL,
    adopted BOOLEAN NOT NULL,
    organization_id VARCHAR(50) REFERENCES organizations(id),
    posting_img_count SMALLINT NULL,
    posting_source VARCHAR(255) NOT NULL,
);

-- Create Attributes table
CREATE TABLE IF NOT EXISTS attributes (
    id SERIAL PRIMARY KEY,
    animal_id BIGINT REFERENCES animals(id) ON DELETE CASCADE,
    spayed_neutered BOOLEAN NULL,
    house_trained BOOLEAN NULL,
    declawed BOOLEAN NULL,
    special_needs BOOLEAN NULL,
    shots_current BOOLEAN NULL
);

-- Create Environment table
CREATE TABLE IF NOT EXISTS environment (
    id SERIAL PRIMARY KEY,
    animal_id BIGINT REFERENCES animals(id) ON DELETE CASCADE,
    dogs_ok BOOLEAN NULL,
    cats_ok BOOLEAN NULL,
    kids_ok BOOLEAN NULL
);
