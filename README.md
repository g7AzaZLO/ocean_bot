# Ocean Bot
<p align="center">
  <img src="https://github.com/user-attachments/assets/ac483550-a12c-4462-8b3c-34b384abf3f6" width="256"/>
</p>
Ocean Bot — это Telegram-бот для работы с API Ocean Protocol, предоставляющий пользователям данные о состоянии узлов сети и другую полезную информацию.

## Возможности

- Получение информации об узлах Ocean Protocol, включая их аптайм.

- Регистрация пользователей в базе данных.

- Интерактивное взаимодействие через Telegram-команды.

## Установка

### 1. Клонирование репозитория

```git clone https://github.com/g7AzaZLO/ocean_bot.git```</br>
```cd ocean_bot```

### 2. Установка зависимостей

Создайте виртуальное окружение и активируйте его:

```python3 -m venv venv```</br>
```source venv/bin/activate ``` # Для Windows: venv\Scripts\activate

## Установите зависимости:

```pip install -r requirements.txt```

### 3. Настройка окружения

Создайте файл .env в корне проекта и укажите следующие переменные:

```BOT_TOKEN=ваш_токен_бота```

Получите BOT_TOKEN у BotFather.

## Запуск

Для запуска бота выполните:

```python app.py```


## Поддерживаемые команды

`/start`

Проверяет наличие пользователя в базе. Если не находит, то просит ввести его IP для отслеживания
![image](https://github.com/user-attachments/assets/81a4f878-0375-464c-a99f-6166ab451dff)

![image](https://github.com/user-attachments/assets/bbb53465-f994-4350-8976-3c6b7da8b6e7)


`/ip`

Если у пользователя уже есть сохраненные IP-адреса, то они будут показаны и предложено ввести новые для замены. Если данных нет, предлагает ввести новые IP-адреса.

![image](https://github.com/user-attachments/assets/3dfd1dc9-a32f-4b4a-8355-a592d3644b65)


`/check`

Получает сохраненные IP-адреса пользователя, вызывает `parse_node` для каждого адреса, собирает данные и отображает информацию о серверах, включая общее количество нод, eligible-нод, их процент, количество нод с аптаймом 90%+ и средний аптайм.

![image](https://github.com/user-attachments/assets/1f4793e9-121b-4dcc-adfe-b39ae6642dce)


`/check_total`

Отображает информацию по всем нодам в сети
![image](https://github.com/user-attachments/assets/3919c093-d11c-4fab-b98b-816332c95ac1)


## Структура проекта

`app.py` — главный файл для запуска бота.

`bot/db.py` — все что связано с базой и взаимодействией с ней.

`bot/logic.py` — логика обработки команд бота.

`config/settings.py` — настройки проекта.

`parser/logic.py` — функции для взаимодействия с API Ocean Protocol.

![image](https://github.com/user-attachments/assets/ec3887ab-0817-4d67-9c57-e64332ef5c33)

## Требования

Python 3.11 или выше.

Библиотеки из requirements.txt.

## Вклад в проект

1. Сделайте форк репозитория.

2. Внесите изменения.

3. Создайте pull request.
