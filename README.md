# school_mos
Эта библиотека позволяет получить легкий доступ к ресурсам Московской Электронной Школы, в обход учебного портала.

### Примечания:

1) Для авторизации используется Selenium (Firefox). Если у вас установлен другой браузер, необходимо установить Firefox либо geckodriver к нему.

2) Библиотека пока не умеет работать с профилем учителя, а также будет выводить информацию только об одном ребенке, в случае, если авторизация происходит через многодетный родительский аккаунт.

3) Для ознакомления с форматом вывода данных рекомендуется просмотреть Types.py

### Установка:
```
pip install school_mos
```

### Авторизация:
1) По логину и паролю:
```
login = ...  # Ваш логин от mos.ru
password = ...  # Ваш пароль

import school_mos

user = school_mos.AUTH(_login=login, _password=password,
                       show_token=True  # необязательный параметр, см. ниже
                       )
```
2) По токену:</br>

   **Рекомендуется использовать именно этот способ, т.к это существенно сокращает время работы из-за ненадобности получения токена c каждой авторизацией (при использовании способа выше).** </br>   
   *Для использования необходимо поставить значение параметра "show_token" на True и сохранить токен после его вывода в консоль*
  ```
token = ...

user = school_mos.AUTH(token=token)
  ```

#### Получение оценок:
1) За определенную дату:
```
print(user.marks.get_by_date(date_offset=1))  # Реализовано путем отступа от текущей даты на n дней
```
2) За триместр / четверть:
```
print(user.marks.get_per_trimester(trimester=0))
# trimester: по умолчанию - первый. При неверно заданном параметре вернёт None
```
#### Получение расписания:
```
print(user.schedule.get_by_date(date_offset=1)
```
#### Получение домашнего задания:
```
print(user.homework.get_by_date(date_offset=1)
```
#### Получение информации о пользователе:
```
print(f'{user.first_name}, {user.birth_date}, {user.class_name} класс\n')
# пример
```   


*Создано в рамках школьного проекта учеником 11-А класса Школы №64 [Выпуск 2023-24]*
