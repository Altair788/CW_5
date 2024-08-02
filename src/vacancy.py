from abc import ABC, abstractmethod


class BaseVacancy(ABC):
    """
    Абстрактный базовый класс для представления вакансии.
    """

    @classmethod
    @abstractmethod
    def new_vacancy(cls, data: dict, company_id: int) -> 'Vacancy':
        """
        Метод для создания нового объекта класса Вакансия.

        Args:
            data(dict): данные по вакансии.
            company_id(int): id работодателя.
        Returns:
            Vacancy: экземпляр класса Вакансия.
        """
        pass


class Vacancy(BaseVacancy):
    """
    Представляет класс Вакансия.
    """
    vacancy_id: str
    name: str
    url: str
    salary: dict
    requirement: str

    def __init__(self, vacancy_id: str, name: str, url: str, salary: dict, requirement: str, company_id: int) -> None:
        """
        Конструктор экземпляра класса Вакансия.
        """
        self.__vacancy_id = vacancy_id if vacancy_id else ""
        self.__name = name if name else ""
        self.__url = url if url else ""
        # Если зарплата не указана, создаем пустой диапазон
        if salary:
            salary_from = salary.get('from', 0) if salary.get('from') is not None else 0
            salary_to = salary.get('to', 0) if salary.get('to') is not None else 0

            self.__salary = {'from': salary_from, 'to': salary_to}
        else:
            self.__salary = {"from": 0, "to": 0}

        self.__requirement = requirement if requirement else ""
        self.__company_id = company_id

        super().__init__()

    @property
    def vacancy_id(self):
        return self.__vacancy_id

    @property
    def name(self):
        return self.__name

    @property
    def url(self):
        return self.__url

    @property
    def salary(self):
        return self.__salary

    @property
    def requirement(self):
        return self.__requirement

    @property
    def company_id(self):
        return self.__company_id

    def __str__(self) -> str:
        """
       Выводит строковое представление объекта класса Вакансия.
        """
        # salary_str = ""
        if self.salary.get("from") and self.salary.get("to"):
            salary_str = f"{self.salary['from']} - {self.salary['to']}"
        else:
            salary_value = self.salary.get("from") or self.salary.get("to")
            salary_str = str(salary_value) if salary_value else ""

        return (f"ID: {self.__vacancy_id}"
                f"Название вакансии: {self.__name}\n"
                f"Ссылка на вакансию: {self.__url}\n"
                f"Зарплата: {salary_str}\n"
                f"Требования к вакансии: {self.__requirement}")

    @classmethod
    def new_vacancy(cls, data: dict, company_id: int) -> 'Vacancy':
        """
        Метод для создания экземпляра класса Вакансия.
        Args:
            data(dict): данные по вакансии.
            company_id(int): ID работодателя.
        Returns:
            Vacancy: экземпляр класса Вакансия.
        """
        salary = data.get("salary")
        if salary:
            salary_from = salary.get('from', 0) if salary.get('from') is not None else 0
            salary_to = salary.get('to', 0) if salary.get('to') is not None else 0
        else:
            # Устанавливаем значения зарплаты по умолчанию, если отсутствует salary
            salary_from, salary_to = 0, 0
        vacancy_id = data.get("id", "")
        name = data.get("name", "")
        url = data.get("url", "")
        salary = {'from': salary_from, 'to': salary_to}
        requirement = data.get("snippet", {}).get("requirement", "")
        company_id = company_id

        return cls(vacancy_id, name, url, salary, requirement, company_id)

    # Метод сравнения вакансий по зарплате
    def compare_salaries(self, other):
        from1 = self.salary.get('from', 0)
        to1 = self.salary.get('to', from1)
        from2 = other.salary.get('from', 0)
        to2 = other.salary.get('to', from2)

        if to1 < from2:
            return -1
        elif from1 > to2:
            return 1
        else:
            return 0

    def __lt__(self, other):
        return self.compare_salaries(other) == -1

    def __eq__(self, other):
        return self.compare_salaries(other) == 0

    def __gt__(self, other):
        return self.compare_salaries(other) == 1

    @classmethod
    def cast_to_object_list(cls, data: list[dict], company_id: int) -> list['Vacancy']:
        """
        Возвращает список экземпляров класса Vacancy.
        Args:
            data(list(dict)): данные, полученные по API.
            company_id(int): id работодателя.
        """
        vacancies_list = []
        for item in data:
            vacancy = cls.new_vacancy(item, company_id)
            vacancies_list.append(vacancy)
        return vacancies_list
    #
    # @staticmethod
    # def create_from_dict_list(vacancies_dict_list: list[dict]) -> list['Vacancy']:
    #     """
    #     Создает список объектов Vacancy из списка словарей.
    #     Args:
    #         vacancies_dict_list (list[dict]): Список словарей, представляющих вакансии.
    #     Returns:
    #         list[Vacancy]: Список объектов Vacancy.
    #     """
    #     vacancies_list = []
    #     for vacancy_dict in vacancies_dict_list:
    #         vacancy = Vacancy(
    #             vacancy_dict["vacancy_id"],
    #             vacancy_dict["name"],
    #             vacancy_dict["url"],
    #             vacancy_dict["salary"],
    #             vacancy_dict["requirement"],
    #             vacancy_dict["company_id"]
    #         )
    #         vacancies_list.append(vacancy)
    #     return vacancies_list
