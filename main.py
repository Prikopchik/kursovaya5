import configparser
from src.functions import (calculate_avg_salary, filter_vacancies_with_higher_salary, format_avg_salary, format_companies_and_vacancies, format_vacancies, format_vacancies_with_higher_salary, get_companies_data, get_vacancies_data, insert_data_to_db, create_tables, check_and_create_database)

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    db_params = {
        'dbname': config['postgres']['database'],
        'user': config['postgres']['user'],
        'password': config['postgres']['password'],
        'host': config['postgres']['host']
    }
    
    db_name = config['postgres']['database']
    
    check_and_create_database(db_params, db_name)
    create_tables(db_params)
    
    companies = ['Skyeng', 'Yandex', 'Mail.ru']
    companies_data = get_companies_data(companies)
    
    vacancies_data = []
    for company in companies_data:
        company_vacancies = get_vacancies_data(company['id'])
        for vacancy in company_vacancies:
            vacancy['company_id'] = company['id']
        vacancies_data.extend(company_vacancies)
    
    insert_data_to_db(companies_data, vacancies_data, db_params)
    
    formatted_companies_and_vacancies = format_companies_and_vacancies(companies_data)
    formatted_vacancies = format_vacancies(vacancies_data)
    avg_salary = calculate_avg_salary(vacancies_data)  # Нужно добавить функцию calculate_avg_salary
    formatted_avg_salary = format_avg_salary(avg_salary)
    vacancies_with_higher_salary = filter_vacancies_with_higher_salary(vacancies_data, avg_salary)  # Нужно добавить функцию filter_vacancies_with_higher_salary
    formatted_vacancies_with_higher_salary = format_vacancies_with_higher_salary(vacancies_with_higher_salary)
    
    print(formatted_companies_and_vacancies)
    print(formatted_vacancies)
    print(formatted_avg_salary)
    print(formatted_vacancies_with_higher_salary)

if __name__ == '__main__':
    main()
