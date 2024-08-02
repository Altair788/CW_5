from abc import ABC, abstractmethod
from typing import Any

import psycopg2

from config import config
from src.api import Parser
from src.employer import Employer
from src.vacancy import Vacancy


class AbstractDBManager(ABC):
    """
    Представляет абстрактный класс AbstractDBManager.
    """
    @abstractmethod
    def create_table(self) -> None:
        """
        Абстрактный метод для создания таблиц.
        """

        pass

    @abstractmethod
    def drop_table(self, table: str) -> None:
        """
        Абстрактный метод для удаления таблицы.

        Args:
             table(str): наименование таблицы.

        """
        pass


class DBManager(AbstractDBManager):
    """
    Представляет класс менеджера БД.
    Наследует функциональность от абстрактного класса AbstractDBManager.
    """

    def __init__(self, dbname: str, user: str, password: str, host: str, port: int):
        # подключение к БД идет 1 раз (так быстрее)
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS companies(
                id SERIAL PRIMARY KEY,
                employer_id TEXT,
                name TEXT NOT NULL,
                alternate_url TEXT,
                city TEXT NOT NULL,
                description TEXT,
                site_url TEXT,
                vacancies_url TEXT,
                open_vacancies INTEGER
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies(
                id SERIAL PRIMARY KEY,
                vacancy_id TEXT,
                name TEXT NOT NULL,
                company_id INTEGER,
                url TEXT NOT NULL,
                salary_min INTEGER,
                salary_max INTEGER,
                requirement TEXT NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );
            """)
        self.conn.commit()

    def insert_data_to_table_and_get_dict_with_employer_id_and_vacancies_url(self, data: list[Vacancy | Employer],
                                                                             table: str) -> dict[int, str]:
        """
        Заполняет таблицу данными и возвращает словарь с данными, где ключом является id работодателя,
        а значением - api - ссылка на вакансии работодателя, для дальнейшего использования по парсингу вакансий
        работодателя и заполнению таблицы vacancies.

        Args:
             data(list[Vacancy | Employer]): список с объектами класса Вакансия или Работодатель
             table(str): наименование таблицы
        Returns:
            dict[int, str]: словарь с данными, где ключом является id работодателя,
            а значением - api - ссылка на вакансии работодателя.
        """
        data_id_and_vacancies_url: dict[int, str] = {}

        if table == "companies":
            with self.conn.cursor() as cur:
                sql = """
                INSERT INTO companies (employer_id, name, alternate_url, city,
                description, site_url, vacancies_url, open_vacancies) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, vacancies_url;
            """
                for item in data:
                    cur.execute(sql, (item.employer_id, item.name,
                                      item.alternate_url, item.city,
                                      item.description, item.site_url, item.vacancies_url, item.open_vacancies))

                    row = cur.fetchone()
                    if row:
                        data_id_and_vacancies_url[row[0]] = row[1]

            self.conn.commit()

        elif table == "vacancies":
            with self.conn.cursor() as cur:
                sql = f"""
                INSERT INTO vacancies (vacancy_id, name, company_id, url, salary_min, salary_max, requirement)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
                for item in data:
                    cur.execute(sql, (item.vacancy_id, item.name, item.company_id, item.url,
                                      item.salary['from'], item.salary['to'], item.requirement))

            self.conn.commit()

        else:
            raise ValueError(f"Таблица '{table}' не найдена.")

        return data_id_and_vacancies_url

    def drop_table(self, table: str) -> None:
        """
        Удаляет таблицу, если она существует.

        Args:
             table(str): наименование таблицы.
        """
        with self.conn.cursor() as cur:
            cur.execute(f"""
                   DROP TABLE IF EXISTS {table};
               """)
        self.conn.commit()

    def get_companies_and_vacancies_count(self) -> list[tuple[Any, ...]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            list[tuple[Any, ...]]: список всех компаний и количество вакансий у каждой компании.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT companies.name, COUNT(vacancies.id)
                    FROM companies
                    LEFT JOIN vacancies ON companies.id = vacancies.company_id
                    GROUP BY companies.name;
                """)

            results: list[tuple[Any, ...]] = cur.fetchall()

        self.conn.commit()

        return results

    def get_all_vacancies(self) -> list[tuple[Any, ...]]:
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии
        и зарплаты и ссылки на вакансию.

        Returns:
            list[tuple[Any, ...]]: список всех вакансий с указанием названия компании, названия вакансии
        и зарплаты и ссылки на вакансию.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT c.name, v.name, v.salary_min, v.salary_max, v.url
                    FROM vacancies as v
                    JOIN companies as c ON v.company_id = c.id;
                """)
            results: list[tuple[Any, ...]] = cur.fetchall()

        self.conn.commit()

        return results if results is not None else "Вакансии не найдены"

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.

        Returns:
            float: Средняя зарплата по вакансиям.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((salary_min + salary_max) / 2.0) AS avg_salary
                FROM vacancies
                WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL;
            """)

            result: tuple[Any, ...] | None = cur.fetchone()
            avg_salary = result[0] if result[0] is not None else 0.0

        return round(avg_salary, 2)

    def get_vacancies_with_higher_salary(self) -> list[tuple[Any, ...]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Returns:
            list[tuple[Any, ...]]: Список вакансий с зарплатой выше средней.
        """
        with self.conn.cursor() as cur:
            # Первый запрос: получаем среднюю зарплату
            cur.execute("""
                SELECT AVG((salary_min + salary_max) / 2.0) AS avg_salary
                FROM vacancies
                WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL;
            """)

            result: tuple[Any, ...] | None = cur.fetchone()
            avg_salary = result[0] if result[0] is not None else 0.0

            # Второй запрос: получаем вакансии с зарплатой выше средней
            cur.execute(f"""
                SELECT c.name, v.name, v.salary_min, v.salary_max, v.url
                FROM vacancies as v
                JOIN companies as c ON v.company_id = c.id
                WHERE (v.salary_min + v.salary_max) / 2.0 > {avg_salary};
            """)

            vacancies_data: list[tuple[Any, ...]] = cur.fetchall()

        return vacancies_data

    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple[Any, ...]]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например, python.

        Args:
            keyword (str): переданное в запрос слово
        Returns:
            list[tuple[Any, ...]]: список всех вакансий, в названии которых содержатся переданные в метод слова.
        """
        with self.conn.cursor() as cur:
            # Используем параметризацию для безопасности
            cur.execute("""
                SELECT c.name, v.name, v.salary_min, v.salary_max, v.url
                FROM vacancies AS v
                JOIN companies AS c ON v.company_id = c.id
                WHERE v.name LIKE %s;
            """, (f'%{keyword}%',))

            vacancies_data: list[tuple[Any, ...]] = cur.fetchall()

        return vacancies_data

#
# if __name__ == "__main__":
#     params = config()
#     db = DBManager(**params)
#     db.create_table()
#
#     hh_api = Parser("https://api.hh.ru/employers")
#     employers_data: list[dict] = hh_api.get_employers()
#     # print(data)
#     employers_list: list[Employer] = Employer.cast_to_object_list(employers_data)
#     print(len(employers_list))
#     data_id_and_vacancies_url = db.insert_data_to_table_and_get_dict_with_employer_id_and_vacancies_url(employers_list,
#                                                                                                         'companies')
#     vacancies_data: list[Vacancy] = hh_api.get_vacancies(data_id_and_vacancies_url)
#     print(len(vacancies_data))
#     db.insert_data_to_table_and_get_dict_with_employer_id_and_vacancies_url(vacancies_data, 'vacancies')
#     print(db.get_companies_and_vacancies_count())
#     print(db.get_all_vacancies())
#     print(db.get_avg_salary())
#     print(db.get_vacancies_with_higher_salary())
#     print(db.get_vacancies_with_keyword('Linux'))
#
#     db.drop_table("vacancies")
#     db.drop_table("companies")
