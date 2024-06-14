import requests
import psycopg2
import configparser

def check_and_create_database(db_params, db_name):
    conn = psycopg2.connect(dbname='postgres', user=db_params['user'], password=db_params['password'], host=db_params['host'])
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database {db_name} created successfully")
    
    cursor.close()
    conn.close()

def create_tables(db_params):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    with open('data/create_db.sql', 'r') as file:
        sql = file.read()
    
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

def get_companies_data(company_names):
    headers = {'User-Agent': 'Mozilla/5.0'}
    companies_data = []
    for company in company_names:
        response = requests.get(f'https://api.hh.ru/employers?text={company}', headers=headers)
        if response.status_code == 200:
            company_data = response.json().get('items', [])[0]
            companies_data.append({
                'id': company_data['id'],
                'name': company_data['name'],
                'url': company_data['alternate_url'],
                'description': company_data.get('description')
            })
    return companies_data

def get_vacancies_data(company_id):
    headers = {'User-Agent': 'Mozilla/5.0'}
    vacancies_data = []
    response = requests.get(f'https://api.hh.ru/vacancies?employer_id={company_id}', headers=headers)
    if response.status_code == 200:
        vacancies = response.json().get('items', [])
        for vacancy in vacancies:
            vacancies_data.append({
                'id': vacancy['id'],
                'name': vacancy['name'],
                'salary_from': vacancy['salary']['from'] if vacancy['salary'] else None,
                'salary_to': vacancy['salary']['to'] if vacancy['salary'] else None,
                'url': vacancy['alternate_url'],
                'description': vacancy.get('snippet', {}).get('requirement')
            })
    return vacancies_data

def insert_data_to_db(companies_data, vacancies_data, db_params):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    for company in companies_data:
        cursor.execute("""
            INSERT INTO companies (id, name, url, description)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (company['id'], company['name'], company['url'], company['description']))
    
    for vacancy in vacancies_data:
        cursor.execute("""
            INSERT INTO vacancies (id, company_id, name, salary_from, salary_to, url, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (vacancy['id'], vacancy['company_id'], vacancy['name'], vacancy['salary_from'], vacancy['salary_to'], vacancy['url'], vacancy['description']))

    conn.commit()
    cursor.close()
    conn.close()

def format_companies_and_vacancies(companies_and_vacancies):
    formatted_output = ["Список компаний и количество вакансий:"]
    for company, count in companies_and_vacancies:
        formatted_output.append(f"{company}: {count} вакансий")
    return "\n".join(formatted_output)

def format_vacancies(vacancies):
    formatted_output = ["Список всех вакансий:"]
    for company, title, salary_from, salary_to, url in vacancies:
        salary = "не указана"
        if salary_from and salary_to:
            salary = f"от {salary_from} до {salary_to} руб."
        elif salary_from:
            salary = f"от {salary_from} руб."
        elif salary_to:
            salary = f"до {salary_to} руб."
        
        formatted_output.append(f"Компания: {company}\nВакансия: {title}\nЗарплата: {salary}\nСсылка: {url}\n")
    return "\n".join(formatted_output)

def format_avg_salary(avg_salary):
    return f"Средняя зарплата по вакансиям: {avg_salary:.2f} руб."

def format_vacancies_with_higher_salary(vacancies):
    formatted_output = ["Вакансии с зарплатой выше средней:"]
    for company, title, salary_from, salary_to, url in vacancies:
        salary = "не указана"
        if salary_from and salary_to:
            salary = f"от {salary_from} до {salary_to} руб."
        elif salary_from:
            salary = f"от {salary_from} руб."
        elif salary_to:
            salary = f"до {salary_to} руб."
        
        formatted_output.append(f"Компания: {company}\nВакансия: {title}\nЗарплата: {salary}\nСсылка: {url}\n")
    return "\n".join(formatted_output)

def calculate_avg_salary(vacancies):
    total_salary = 0
    count = 0
    for vacancy in vacancies:
        if vacancy['salary_from'] and vacancy['salary_to']:
            avg_salary = (vacancy['salary_from'] + vacancy['salary_to']) / 2
            total_salary += avg_salary
            count += 1
        elif vacancy['salary_from']:
            total_salary += vacancy['salary_from']
            count += 1
        elif vacancy['salary_to']:
            total_salary += vacancy['salary_to']
            count += 1
    return total_salary / count if count > 0 else 0

def filter_vacancies_with_higher_salary(vacancies, avg_salary):
    return [vacancy for vacancy in vacancies if (vacancy['salary_from'] and vacancy['salary_from'] > avg_salary) or (vacancy['salary_to'] and vacancy['salary_to'] > avg_salary)]
