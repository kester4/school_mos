# school_mos
Эта библиотека позволяет получить легкий доступ к ресурсам Московской Электронной Школы, в обход учебного портала.

### Примечания:

1) Для авторизации используется Selenium (Firefox). Если у вас установлен другой браузер, необходимо установить Firefox либо geckodriver к нему.

2) Библиотека пока не умеет работать с профилем учителя, а также будет выводить информацию только об одном ребенке, в случае, если авторизация происходит через многодетный родительский аккаунт.

### Установка:
```
pip install -r requirements.txt
```

### Использование:
```
login = '' # Ваш логин от mos.ru
password = '' # Ваш пароль

import school_mos
user = school_mos.AUTH(_login=login, _password=password)
```
Получение оценок (Для ознакомления с содержание типов в выводе рекомендуется просмотреть Types.py):
```
print(user.marks.get_by_date(date_offset=1) # Реализовано путем отступа от текущей даты на n дней
```
Расписания:
```
print(user.schedule.get_by_date(date_offset=1)
```
Домашнего задания:
```
print(user.homework.get_by_date(date_offset=1)
```
Информации о пользователе:
```
print(f'{user.user_firstName}, {user.user_birthD}, {user.user_class_name} класс\n')
# пример
```


*Создано в рамках школьного проекта учеником 11-А класса ~Шарашки~ Школы №64 [2023-24]*
