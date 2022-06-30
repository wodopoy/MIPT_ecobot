# MIPT_ecobot
Project for exam 2022. MIPT eco bot by Samanyuk Evelina, Makarova Anastasia, Konyahina Uliana, Shirvanyan Lida

Этот бот помогает найти оптимальное расстояние и наилучший день недели для вызова Экотакси. Он обрабатывает данные пользователей: количество отходов, адрес и удобные для пользователя дни недели чтобы подойти и сдать мусор, а затем делает рассылку с наилучшей датой для вызова Экотакси и с двумя адресами: координаты места, средневзвешенно-удаленного от всех пользователей, и ближайший к этим координатам адрес среди всех пользователей.

Структура проекта:
```
.
├── auxiliaryfunc.py
├── bot.py
├── configStore.sh
├── db.sqlite
├── dbworker.py
├── helper
│   └── dbCreate.py
└── yandexmap.py
```
| Название файла | Описание |
| ------ | ------ |
| bot.py | основное тело тг бота |
| dbworker.py | работа с базами данных |
| auxiliaryfunc.py | файл с функциями для расчета лучшего дня и лучшей точки |
| yandexmap.py | работа с api yandex map  |
| configStore.sh & helper/ db.Create.py | это вспомогательный скрипт для работы с бд sqlite3 при отладке |
| db.sqlite | файл бд |
| .env | енв файл с ключами апи |
