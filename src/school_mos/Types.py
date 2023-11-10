from pydantic import BaseModel


class HouseworkType(BaseModel):
    subject_name: str
    description: str
    attached_tests: list
    attached_files: list


class ScheduleType(BaseModel):
    subject_name: str
    lesson_time: str
    marks: list | None = None
    room_number: str | None = None


class BaseMarkType(BaseModel):
    subject_name: str
    values: list


class TrimesterMarkType(BaseModel):
    subject_name: str
    average_mark: str
    values: list
