# Edupage Timetable Viewer

Удобное веб-приложение для просмотра расписания уроков из Edupage для Нарвской Гимназии. Проект был создан за один вечер как альтернатива официальному интерфейсу, предлагая более простой и удобный просмотр расписания.

![Table Preview](static/images/table.png)

## 🔍 Функциональность

- Просмотр расписания классов Нарвской Гимназии
- Переключение между классами через удобное меню
- Поддержка тёмной темы для комфортного использования в любое время суток
- Мобильная версия с адаптивным дизайном и навигацией
- Отображение нескольких вариантов уроков в одной ячейке расписания
- Отображение важной информации об уроках (учителя, кабинеты)

## 🛠️ Технические детали

Проект использует следующие технологии:

- **Backend**: Python с фреймворком Flask
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Шаблонизатор**: Jinja2
- **API**: Интеграция с Edupage API для получения данных расписания

## ⚠️ Ограничения

Проект был создан быстро и имеет некоторые ограничения:

- Длинные уроки могут отображаться некорректно (время начала правильное, но время окончания может быть неверным)
- Реализован только просмотр расписания классов, без поддержки просмотра по учителям, кабинетам или предметам
- Другие разделы кроме расписания классов пока не реализованы

## 🚀 Установка и запуск

### Предварительные требования

- Python 3.7+
- pip (менеджер пакетов Python)

### Шаги по установке

1. Клонировать репозиторий:
```bash
git clone https://github.com/MONZikWasTaken/NARGTab.git
cd nargtab
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Запустить приложение:
```bash
python app.py
```

4. Открыть в браузере:
```
http://localhost:5000
```

## 📱 Мобильная версия

Приложение полностью адаптировано для мобильных устройств с удобным интерфейсом и гамбургер-меню для навигации между классами.

## 🔄 Будущие улучшения

- Добавление просмотра расписания по учителям
- Добавление просмотра расписания по кабинетам
- Добавление просмотра расписания по предметам
- Улучшение отображения длинных уроков
- Добавление поиска по расписанию

## 👤 Контакты

Если у вас есть вопросы, предложения или вы заметили ошибку, вы можете связаться со мной:

- **Телеграм**: [@MONZikxD](https://t.me/MONZikxD)
- **GitHub**: [MONZikWasTaken](https://github.com/MONZikWasTaken)

## 📄 Лицензия

MIT License 
