from abc import ABC, abstractmethod


class BaseEmployer(ABC):
    """
    Представляет абстрактный класс Работодатель.
    """

    @classmethod
    @abstractmethod
    def new_employer(cls, data: dict) -> 'Employer':
        """
        Метод для создания нового объекта класса Работодатель.
        Args:
            data(dict): данные по работодателям
        Returns:
            Employer: экземпляр класса Работодатель.
        """
        pass


class Employer(BaseEmployer):
    """
    Представляет класс Работодатель.
    """
    employer_id: str
    name: str
    alternate_url: str
    city: str
    description: str
    site_url: str
    vacancies_url: str
    open_vacancies: int

    def __init__(self, employer_id: str, name: str, alternate_url: str, city: str,
                 description: str, site_url: str, vacancies_url: str, open_vacancies: int) -> None:
        super().__init__()
        """
        Конструктор экземпляра класса Работодатель.
        """
        self.__employer_id = employer_id if employer_id else ""
        self.__name = name if name else ""
        self.__alternate_url = alternate_url if alternate_url else ""
        self.__city = city if city else ""
        self.__description = description if description else ""
        self.__site_url = site_url if site_url else ""
        self.__vacancies_url = vacancies_url if vacancies_url else ""
        self.__open_vacancies = open_vacancies if open_vacancies else 0

    @property
    def employer_id(self):
        return self.__employer_id

    @property
    def name(self):
        return self.__name

    @property
    def alternate_url(self):
        return self.__alternate_url

    @property
    def city(self):
        return self.__city

    @property
    def description(self):
        return self.__description

    @property
    def site_url(self):
        return self.__site_url

    @property
    def vacancies_url(self):
        return self.__vacancies_url

    @property
    def open_vacancies(self):
        return self.__open_vacancies

    def __str__(self) -> str:
        """
       Выводит строковое представление объекта класса Работодатель.
        """

        return (f"Данные по работодателю с ID {self.__employer_id}\n"
                f"Наименование: {self.__name}\n"
                f"Описание: {self.__description}\n"
                f"Город: {self.__city}\n"
                f"Ссылка на страницу компании: {self.__site_url}\n"
                f"Всего открытых вакансий компании {self.__open_vacancies}\n"
                f"Ссылка на страницу с вакансиями компании: {self.__alternate_url}\n\n")

    @classmethod
    def new_employer(cls, data: dict) -> 'Employer':
        """
        Метод для создания экземпляра класса Работодатель.
        Args:
            data(dict): данные, полученные при обращении к API.
        Returns:
            Employer: экземпляр класса Работодатель.
        """
        employer_id = data.get("id", "")
        name = data.get("name", "")
        alternate_url = data.get("alternate_url", "")
        city = data.get("area", {}).get("name", "")
        description = data.get("description", "")
        site_url = data.get("site_url", "")
        vacancies_url = data.get("vacancies_url", "")
        open_vacancies = data.get("open_vacancies", 0)

        return cls(employer_id, name, alternate_url, city, description, site_url, vacancies_url, open_vacancies)

    @classmethod
    def cast_to_object_list(cls, data: list[dict]) -> list['Employer']:
        """
        Возвращает список экземпляров класса Employer.
        Args:
            data(list(dict)): данные, полученные по API.
        """
        employers_list = []
        for i in data:
            employer = cls.new_employer(i)
            employers_list.append(employer)
        return employers_list
