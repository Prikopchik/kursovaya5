import requests
import psycopg2
import configparser

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
