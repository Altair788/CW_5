from pathlib import Path
from configparser import ConfigParser

ROOT_PATH = Path(__file__).parent

DATABASE_INI_PATH = ROOT_PATH.joinpath("data", "database.ini")

favorite_companies_id_hh = ['3529', '78638', '906557', '9498112', '4649269', '5390761',
                            '6189', '3125', '26624', '15478', '2180', '1057',
                            '3776', '2733062', '1740', '87021', '4233', '740']

params_for_getting_employers = {"text": "",
                                "page": 0,
                                "per_page": 100,
                                "only_with_vacancies": "true",
                                "sort_by": "by_name"}

params_for_getting_vacancies = {"text": "",
                                "page": 0,
                                "per_page": 100,
                                "only_with_salary": "true"}


def config(filename=DATABASE_INI_PATH, section="postgresql") -> dict[str, str]:
    """
    Конфигурируем БД из файла по ссылке (считываем конфигурационный файл).
    Args:
         filename(Path): конфигурационные данные БД postgresql
         section(str): секция в конфигурационном файле
    Returns:
        db(dict): словарь с параметрами соединения, которые будут передаваться в DBManager() в дальнейшем.
    """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql

    db_params = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_params[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} is not found in the {filename} file.')
    return db_params
