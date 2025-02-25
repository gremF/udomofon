# Интеграция открытия двери домофона Ufanet в Home Assistant

1. **Добавить следующий код в файл `configuration.yaml`:**

   ```yaml
   shell_command:
     open_udomofon: "python3 /config/python_scripts/udomofon.py"
   ```

   и:

   ```yaml
   python_script:
   ```

2. **Создать папку и файлы:**

   - в корневом разделе `config` Home Assistant создат папку `python_scripts`

   - файлы `udomofon_log.txt` и `secrets.yaml`

   - поместить файл `udomofon.py` из данного репозитория в папку `python_scripts`

3. **Настроить получение данных для авторизации:**

   Файл `secrets.yaml` содержит данные авторизации. Добавить в него логин и пароль Ufanet:

   ```yaml
   login: Ваш логин/номер договора
   password: "Ваш пароль"
   ```

4. **Реализация в Home Assistant данной интеграции как исполняемый скрипт:**

   Добавить скрипт в `configuration.yaml`:

   ```yaml
   script:
     udomofon_open_door:
       alias: "Открыть дверь"
       sequence:
         - service: shell_command.open_udomofon
   ```
