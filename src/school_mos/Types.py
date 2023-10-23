from pydantic import BaseModel


class HouseworkType(BaseModel):
    description: str
    subject_name: str
    attached_test: str | None = None
    attached_file: str | None = None


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
