# check-urls

`check-urls` — это Python-приложение для проверки доступности URL-адресов из файла и записи успешных в выходной файл.

## Структура проекта
```
check_urls/
│── cli.py          # CLI-команда для запуска проверки
│── core.py         # Основная логика обработки URL
│── http_client.py  # HTTP-клиент на основе requests
│── status_handler.py # Обработчик статусов HTTP
│── __main__.py     # Точка входа в программу
│── requirements.txt # Список зависимостей
│── README.md       # Документация
```

## Возможности

- Проверка списка URL-адресов на доступность с использованием `requests`.
- Обработка HTTP-статусов:
  - **Успешные (2xx)**: Запись URL в файл.
  - **Редиректы (3xx)**: Переход по новому адресу и проверка доступности.
  - **Ошибки (4xx, 5xx)**: Логирование ошибки.
- Ввод и вывод файлов задаются через аргументы командной строки.

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/panisimov812/PythonProject.git
cd check-urls
```

## Создание виртуального окружения
```
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate     # Для Windows
```
## Установка зависимостей
```
pip install -r requirements.txt
```

## Запуск
```
python -m check_urls.cli --input <путь_к_входному_файлу> --output <путь_к_выходному_файлу>
Пример
python -m check_urls.cli --input urls.txt --output successful_urls.txt
```