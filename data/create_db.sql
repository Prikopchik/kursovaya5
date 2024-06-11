CREATE DATABASE hh_database;

\c hh_database

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255),
    description TEXT
);

CREATE TABLE vacancies (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    salary_from INTEGER,
    salary_to INTEGER,
    url VARCHAR(255),
    description TEXT
);
