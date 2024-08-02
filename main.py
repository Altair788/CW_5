from config import config
from src.dbmanager import DBManager
from src.api import Parser
from src.employer import Employer
from src.vacancy import Vacancy


def interact_with_user():
    """
        Функция для взаимодействия с пользователем и управления работой программы.

        Функция предоставляет пользователю меню с различными действиями, такими как:
        - Получение списка всех компаний и количества вакансий у каждой компании
        - Получение списка всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки
         на вакансию
        - Получение средней зарплаты по вакансиям.
        - Получение списка всех вакансий, у которых зарплата выше средней по всем вакансиям
        - Получение списка всех вакансий, в названии которых содержится ключевое слово
        - Завершение программы

        Пользователь может выбирать действие, вводя соответствующий номер, и программа будет
        выполнять выбранное действие.
        """
    params = config()
    db = DBManager(**params)
    db.create_table()

    hh_api = Parser("https://api.hh.ru/employers")

    employers_data: list[dict] = hh_api.get_employers()
    employers_list: list[Employer] = Employer.cast_to_object_list(employers_data)
    data_id_and_vacancies_url = db.insert_data_to_table_and_get_dict_with_employer_id_and_vacancies_url(employers_list,
                                                                                                        'companies')
    vacancies_data: list[Vacancy] = hh_api.get_vacancies(data_id_and_vacancies_url)
    db.insert_data_to_table_and_get_dict_with_employer_id_and_vacancies_url(vacancies_data, 'vacancies')

    while True:
        print("\nВыберите действие:")
        print("1. Получить список всех компаний и количество вакансий у каждой компании.")
        print("2. Получить список всех вакансий с указанием названия компании, "
              "названия вакансии и зарплаты и ссылки на вакансию.")
        print("3. Получить среднюю зарплату по вакансиям.")
        print("4. Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям.")
        print("5. Получить список всех вакансий, в названии которых содержится ключевое слово.")
        print("6. Завершить программу.")

        user_choice = input("Введите номер действия: ")

        if user_choice == "1":
            print(db.get_companies_and_vacancies_count())
        elif user_choice == "2":
            print(db.get_all_vacancies())
        elif user_choice == "3":
            print(db.get_avg_salary())
        elif user_choice == "4":
            print(db.get_vacancies_with_higher_salary())
        elif user_choice == "5":
            search_query = input("Введите ключевое слово: ")
            print(db.get_vacancies_with_keyword(search_query))
        elif user_choice == "6":
            db.drop_table("vacancies")
            db.drop_table("companies")
            print("Программа завершена.")
            break

        else:
            print("Некорректный ввод. Повторите попытку.")


if __name__ == "__main__":
    interact_with_user()
