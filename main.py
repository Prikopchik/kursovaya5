import configparser
from src.functions import get_companies_data, get_vacancies_data, insert_data_to_db, create_tables
from src.DBManager import DBManager

def main():
    config = configparser.ConfigParser()
    config.read('data/config.ini', encoding='utf-8')

    db_params = {
        'host': config['postgresql']['host'],
        'database': config['postgresql']['database'],
        'user': config['postgresql']['user'],
        'password': config['postgresql']['password']
    }

    create_tables(db_params)

    company_names = ["Яндекс", "Сбербанк", "Mail.ru Group", "МТС", "Тинькофф",
                     "Газпром", "Лукойл", "Ростелеком", "Альфа-Банк", "Росатом"]
    
    companies_data = get_companies_data(company_names)
    vacancies_data = []

    for company in companies_data:
        vacancies = get_vacancies_data(company['id'])
        for vacancy in vacancies:
            vacancy['company_id'] = company['id']
        vacancies_data.extend(vacancies)
    
    insert_data_to_db(companies_data, vacancies_data, db_params)
    
    db_manager = DBManager()
    print(db_manager.get_companies_and_vacancies_count())
    print(db_manager.get_all_vacancies())
    print(db_manager.get_avg_salary())
    print(db_manager.get_vacancies_with_higher_salary())
    print(db_manager.get_vacancies_with_keyword('Python'))

if __name__ == '__main__':
    main()
