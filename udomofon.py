import requests
import json
from datetime import datetime
import yaml
from typing import Dict, Union, Optional


def load_secrets() -> Dict[str, str]:
    """
    Чтение логина и пароля из файла secrets.yaml.
    """
    try:
        with open("/config/secrets.yaml", "r") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        raise RuntimeError("Файл secrets.yaml не найден")
    except yaml.YAMLError as error:
        raise RuntimeError(f"Ошибка при чтении YAML-файла: {error}")


def authenticate_and_fetch_data() -> str:
    """
    Получение данных через API.
    """
    try:
        secrets = load_secrets()
    except RuntimeError as error:
        return str(error)

    login_url = "https://dom.ufanet.ru/api-auth/login/?next=/api/v0/skud/shared"
    credentials = {
        'username': secrets.get('login'),
        'password': secrets.get('password')
    }

    if not credentials['username'] or not credentials['password']:
        return "Логин или пароль не заданы в secrets.yaml"

    with requests.Session() as session:
        try:
            # Выполнение GET-запроса для получения CSRF-токена
            response = session.get(login_url)
            response.raise_for_status()
            csrf_token = session.cookies.get('csrftoken')

            if not csrf_token:
                return "CSRF-токен не найден"

            headers = {
                'X-CSRFToken': csrf_token,
                'Referer': login_url,
                'Accept': 'application/json'
            }

            # Выполнение POST-запроса для авторизации
            auth_response = session.post(login_url, data=credentials, headers=headers)
            auth_response.raise_for_status()

            # Получение ID для последующих запросов
            id_url = "https://dom.ufanet.ru/api/v0/skud/shared"
            id_response = session.get(id_url, headers=headers)
            id_response.raise_for_status()

            id_data: Union[Dict, list] = id_response.json()
            if not isinstance(id_data, list) or not id_data:
                return "Ответ не содержит ID или не является списком"

            entity_id: Optional[int] = id_data[0].get('id')
            if entity_id is None:
                return "ID не найден в первом элементе списка"

            # Выполнение запроса на открытие двери
            open_url = f"https://dom.ufanet.ru/api/v0/skud/shared/{entity_id}/open/"
            data_response = session.get(open_url, headers=headers)
            data_response.raise_for_status()

            data: Dict = data_response.json()
            return (
                f"Запрос на открытие двери выполнен успешно. "
                f"Данные: {json.dumps(data)}"
            )

        except requests.RequestException as error:
            return f"Ошибка сети: {error}"
        except ValueError:
            return "Ответ не соответствует формату JSON"


def main() -> None:
    """
    Главная функция.
    """
    result: str = authenticate_and_fetch_data()
    current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Запись результата в log-файл с указанием даты и времени
        with open("/config/udomofon_log.txt", "a") as log_file:
            log_file.write(f"[{current_time}] {result}\n")
    except IOError as error:
        print(f"Ошибка записи log-файла: {error}")


if __name__ == "__main__":
    main()
