CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255),
    description TEXT
);

CREATE TABLE IF NOT EXISTS vacancies (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    salary_from INT,
    salary_to INT,
    url VARCHAR(255),
    description TEXT
);
