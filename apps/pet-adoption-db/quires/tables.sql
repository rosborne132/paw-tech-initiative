-- Create ENUM types
CREATE TYPE age_enum AS ENUM ('kitten', 'adult', 'senior', 'unknown');
CREATE TYPE species_enum AS ENUM ('dog', 'cat');
CREATE TYPE size_enum AS ENUM ('small', 'medium', 'large');
CREATE TYPE status_enum AS ENUM ('available', 'adopted', 'pending');
CREATE TYPE sex_enum AS ENUM ('male', 'female');

-- Create Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL
);

-- Create Animals table
CREATE TABLE IF NOT EXISTS animals (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age age_enum NOT NULL,
    species species_enum NOT NULL,
    breed VARCHAR(100) UNIQUE,
    sex sex_enum NOT NULL,
    size size_enum NOT NULL,
    description TEXT NULL,
    status status_enum NOT NULL,
    organization_id VARCHAR(50) REFERENCES organizations(id),
    posting_img_count SMALLINT NULL
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
