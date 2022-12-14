![Python](https://img.shields.io/badge/Python-14354C?style=badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=badge&logo=docker&logoColor=white)

# EUAutoBot

EUAutoBot - телеграм-бот для расчёта таможенной стоимости импортных автомобилей.

# Запуск

Перед запуском необходимо создать *.env* файл в корневой директории проекта.
Данный файл должен содержать переменные *API_KEY* и *BOT_ADMIN_PASSWORD*, отвечающие за бот-токен и пароль к админке бота, соотвественно.

Для запуска бота через docker необходимо перейти в директорию проекта и воспользоваться следующей командой:

```
docker compose up 
```

# Остановка бота

Для остановки бота нужно ввести команду:
```
docker compose down
```

Для удаления всех volumes, связанных с компоузом:
```
docker compose down -v
```
