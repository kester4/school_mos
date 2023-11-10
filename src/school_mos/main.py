from requests import get
from .errors import *
from .user_auth import _Token
from datetime import date, timedelta
from .Types import *
from collections import defaultdict
from re import sub

MARK_WEIGHTS_SYMBOLS = {1: '\u00B9', 2: '\u00B2', 3: '\u00B3', 4: '\u2074', 5: '\u2075'}
EXLIST = ['marks', 'homework', 'absence_reason_id', 'health_status', 'nonattendance_reason_id']
BINDING_TEST_URL = 'https://uchebnik.mos.ru/exam/launch/specification/{}?material_type=TestSpecification&mode=preview&'


class AUTH:
    def __init__(self, _login=None, _password=None, token=None, show_token=False):
        if token is not None and _password is None and _login is None:
            self.token = token
        elif token is None and _password is not None and _login is not None:
            self.token = _Token.obtain(login=_login, password=_password)
        else:
            raise ValueError('Неверно переданы данные. Необходим либо только токен, либо пара логин + пароль')

        if show_token:
            print(self.token)

        user_data = self.parse_new_user()
        self.user_id = user_data['id']
        self.person_id = user_data['contingent_guid']
        self.first_name = user_data['first_name']
        self.middle_name = user_data.get('middle_name')
        self.last_name = user_data['last_name']
        self.birth_date = user_data['birth_date']
        self.class_level = user_data['class_level_id']
        self.class_name = user_data['class_name']
        self.snils = user_data.get('snils')
        self.user_school = user_data['school']['short_name']
        self.parents = [f"{parent.get('first_name')} {parent.get('last_name')}"
                        for parent in user_data.get('representatives', [{}])]
        self.subjects = {item['subject_id']: sub(r'\s*\b\d{1,2}-?[А-Яа-я]\b', '', item['name'])
                         for item in user_data['groups']}

        self.schedule = _Schedule(self)
        self.marks = _Marks(self)
        self.homework = _Homework(self)

    def parse_new_user(self):
        result = get(
            f"https://school.mos.ru/api/family/web/v1/profile",
            headers={
                'Auth-Token': self.token,
                'Authorization': self.token,
                'X-mes-subsystem': 'familyweb'
            })
        if result.status_code == 200:
            return result.json()['children'][0]

        raise RequestError(result.status_code)


class _Schedule:

    def __init__(self, api_instance):
        self.user = api_instance

    def get_by_date(self, date_offset: int = 0):
        schedule_date = date.today() + timedelta(days=date_offset)
        result = []
        data = get(
            f'https://school.mos.ru/api/eventcalendar/v1/api/events?person_ids={self.user.person_id}&begin_date='
            f'{schedule_date}&end_date={schedule_date}&expand={",".join(EXLIST)}',
            headers={
                "Auth-Token": self.user.token,
                "Profile-Id": f'{self.user.user_id}',
                "authorization": f"Bearer {self.user.token}",
                "x-mes-role": "student",
                "x-mes-subsystem": "familyweb"
            })
        if data.status_code != 200:
            raise RequestError(data.status_code)

        response = data.json()['response']
        if not response:
            raise NullFieldError

        for lesson in response:
            if lesson.get('source') == 'AE':
                continue
            result.append(
                ScheduleType(
                    lesson_time=f'{lesson["start_at"][11:16]} - {lesson["finish_at"][11:16]}',
                    subject_name=lesson.get('subject_name', None),
                    marks=self._parse_marks_from_lesson(lesson["marks"]) if lesson.get("marks") else None,
                    room_number=lesson.get('room_number', None)
                )
            )
        return result

    @staticmethod
    def _parse_marks_from_lesson(marks) -> list[str]:
        marksList = []
        for mark in marks:
            marksList.append(f'{mark["value"]}{MARK_WEIGHTS_SYMBOLS[mark["weight"]]}')
        return marksList


class _Marks:
    def __init__(self, api_instance):
        self.user = api_instance
        self.mark_dict_output = defaultdict(list)

        self.token = self.user.token

    def get_by_date(self, date_offset: int = 0):
        date_to_get = date.today() + timedelta(days=date_offset)
        data = get(
            f'https://dnevnik.mos.ru/core/api/marks?created_at_from={date_to_get}&created_at_to={date_to_get}'
            f'&student_profile_id={self.user.user_id}',
            headers={
                'Auth-Token': self.token,
                'Authorization': self.token
            })

        if data.status_code != 200:
            raise RequestError

        data = data.json()
        if not data:
            raise NullFieldError

        weight_symbols = {mark["weight"]: MARK_WEIGHTS_SYMBOLS[mark["weight"]] for mark in data}

        value_dict = defaultdict(list)
        for mark in data:
            mark_id = mark['subject_id']
            value = mark["values"][0]["grade"]["origin"] + weight_symbols[mark["weight"]]
            value_dict[mark_id].append(value)

        return [
            BaseMarkType(subject_name=self.user.subjects.get(mark_id, ''), values=values)
            # date=mark['created_at'][:10])
            for
            mark_id, values in
            value_dict.items()]

    def get_per_trimester(self, trimester: int = 0):
        data = get(
            f'https://dnevnik.mos.ru/reports/api/progress/json?academic_year_id='
            f'{self.user.class_level}&student_profile_id={self.user.user_id}',
            headers={
                'Auth-Token': self.token,
                'Authorization': self.token
            })
        if data.status_code != 200:
            raise RequestError

        data = data.json()
        try:
            results = {
                item['subject_name']: [
                                          value['original'] + MARK_WEIGHTS_SYMBOLS[mark["weight"]]
                                          for mark in item['periods'][trimester]['marks']
                                          for value in mark['values']
                                      ] + [item['avg_five']]
                for item in data if item['periods']
            }

        except (IndexError, ValueError):
            return None

        return [TrimesterMarkType(subject_name=subject, values=values[:-1], average_mark=values[-1])
                for subject, values in results.items()]


class _Homework:
    def __init__(self, api_instance):
        self.user = api_instance

    def get_by_date(self, date_offset: int = 0):
        date_to_get = date.today() + timedelta(days=date_offset)
        result = []
        data = get(
            f"https://school.mos.ru/api/family/web/v1/homeworks?from={date_to_get}&to={date_to_get}&"
            f"student_id={self.user.user_id}",
            headers={
                "Cookie": f"auth_token={self.user.token};student_id={self.user.user_id}",
                'Auth-Token': self.user.token,
                'x-mes-subsystem': "familyweb"
            }
        )
        if data.status_code != 200:
            raise RequestError(data.status_code)

        payload = data.json()['payload']

        if not payload:
            raise NullFieldError
        for item in payload:
            material = item.get('additional_materials', [{}])
            result.append(
                HouseworkType(
                    subject_name=item.get('subject_name', ''),
                    description=sub(r'\n{2,}', '\n', item["description"]),
                    attached_files=[item['link'] for shit in material if shit['type'] == 'attachments'
                                    for item in shit['items']],
                    attached_tests=[item['urls'][0]['url'] for shit in material if shit['type'] == 'test_spec_binding'
                                    for item in shit['items']]
                )
            )
        return result
