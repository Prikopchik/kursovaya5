import psycopg2
import configparser

class DBManager:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('data/config.ini', encoding='utf-8')
        self.conn = psycopg2.connect(
            host=config['postgresql']['host'],
            database=config['postgresql']['database'],
            user=config['postgresql']['user'],
            password=config['postgresql']['password']
        )
    
    def get_companies_and_vacancies_count(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT companies.name, COUNT(vacancies.id)
            FROM companies
            JOIN vacancies ON companies.id = vacancies.company_id
            GROUP BY companies.name;
        """)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_all_vacancies(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
            FROM vacancies
            JOIN companies ON vacancies.company_id = companies.id;
        """)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_avg_salary(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT AVG((salary_from + salary_to) / 2)
            FROM vacancies
            WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL;
        """)
        result = cursor.fetchone()
        cursor.close()
        return result[0]
    
    def get_vacancies_with_higher_salary(self):
        avg_salary = self.get_avg_salary()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
            FROM vacancies
            JOIN companies ON vacancies.company_id = companies.id
            WHERE (vacancies.salary_from + vacancies.salary_to) / 2 > %s;
        """, (avg_salary,))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_vacancies_with_keyword(self, keyword):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
            FROM vacancies
            JOIN companies ON vacancies.company_id = companies.id
            WHERE vacancies.name ILIKE %s;
        """, ('%' + keyword + '%',))
        result = cursor.fetchall()
        cursor.close()
        return result
