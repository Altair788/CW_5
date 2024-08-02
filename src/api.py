from abc import ABC, abstractmethod
from typing import Any

import requests

from config import favorite_companies_id_hh, params_for_getting_employers, params_for_getting_vacancies
from src.vacancy import Vacancy


class API(ABC):
    """
    Представляет абстрактный класс API.
    """

    @abstractmethod
    def get_employers(self) -> list[dict]:
        """
        Абстрактный метод для получения всех работодателей.
        """

        pass

    @abstractmethod
    def get_vacancies(self, data: dict[int, str]) -> list[Vacancy]:
        """
        Абстрактный метод для получения всех вакансий.
        Args:
            data(dict[int, str]): словарь с данными, где ключом является id работодателя,
            а значением - api - ссылка на вакансии работодателя.
        """
        pass


class Parser(API):
    """
    Представляет класс для парсинга и обработки данных по вакансиям.

    Наследует функциональность от абстрактного класса API.
    """

    def __init__(self, url: str) -> None:
        """
        Метод для инициализации класса API.
        """
        self.__url: str = url
        self.__headers: dict = {"User-Agent": "HH-User-Agent"}
        self.__params: dict = {"text": "", "page": 0, "per_page": 100}
        self.__vacancies: list[dict] = []
        self.__favorite_companies_id_hh: list[str] = favorite_companies_id_hh

    @property
    def url(self):
        return self.__url

    @property
    def headers(self):
        return self.__headers

    @property
    def params(self):
        return self.__params

    @property
    def vacancies(self):
        return self.__vacancies

    @vacancies.setter
    def vacancies(self, new_data: list):
        for vacancy in new_data:
            self.__vacancies.append(vacancy)

    @property
    def favorite_companies_id_hh(self):
        return self.__favorite_companies_id_hh

    def get_employers(self) -> list[dict]:
        """
        Метод для получения работодателей в формате JSON.
        Returns:
            list[dict]: Список с работодателями в формате JSON.
        """
        self.__params = params_for_getting_employers

        employers_data_list: list[dict] = []
        for employer_id in self.__favorite_companies_id_hh:
            response = requests.get(f'https://api.hh.ru/employers/{employer_id}', params=self.__params)
            response.raise_for_status()  # Проверяем статус ответа, вызывает исключение для ошибок HTTP
            data_employer = response.json()
            employers_data_list.append(data_employer)

        return employers_data_list

    def get_vacancies(self, data: dict[int, str]) -> list[Vacancy]:
        """
        Метод для получения вакансий в формате JSON.
        Args:
            data(dict[int, str]): словарь с данными, где ключом является id работодателя,
            а значением - api - ссылка на вакансии работодателя.
        Returns:
            list[Vacancy]: Список с объектами класса Вакансия.
        """
        try:
            vacancies_data_list: list[Vacancy] = []

            self.__params = params_for_getting_vacancies

            for key, value in data.items():
                self.__url = value
                response = requests.get(self.__url, params=self.__params)
                response.raise_for_status()  # Проверяем статус ответа, вызывает исключение для ошибок HTTP
                vacancies: list[dict[str, Any]] = response.json()['items']
                employer_vacancies: list[Vacancy] = Vacancy.cast_to_object_list(vacancies, key)
                vacancies_data_list.extend(employer_vacancies)

            return vacancies_data_list

        except requests.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
