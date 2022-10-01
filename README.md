![Python](https://img.shields.io/badge/Python-14354C?style=badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=badge&logo=docker&logoColor=white)

# EUAutoBot

EUAutoBot - телеграм-бот для расчёта таможенной стоимости импортных автомобилей.

# Запуск

Перед запуском необходимо создать config.env файл в корневой директории проекта.
Данный файл должен содержать переменные API_KEY и BOT_ADMIN_PASSWORD, отвечающие за бот-токен и пароль к админке бота, соотвественно.

Для запуска бота через docker необходимо воспользоваться следующими командами

```
cd [PATH]
docker build [PATH]
docker run -d [IMAGE]
```

# Остановка бота

Для остановки бота нужно ввести команду
```
docker stop [CONTAINER_ID]
```
