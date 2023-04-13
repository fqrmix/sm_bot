from datetime import datetime
from dataclasses import dataclass
from .exceptions import ValueIsNotPresented
from typing import Union, List, Any

@dataclass
class DatabaseObject:
    rows: List[tuple[Any, ...]]
    columns: List[str]

    def get_dict(self):
        if self.rows and self.columns:
            result = []
            for row in self.rows:
                dict_row = {}
                for index, column in enumerate(self.columns):
                    dict_row[column] = row[index]
                result.append(dict_row)
            return result

@dataclass
class DatabaseModel:
    def get_dict(self):
        _class_vars = vars(self)
        _dict = {}
        for _self_var_name, _self_var_value in zip(_class_vars.keys(), _class_vars.values()):
            try:
                assert(_self_var_value is not ...)
                _dict[_self_var_name] = _self_var_value
            except AssertionError:
                raise ValueIsNotPresented(
                    f'Variable "{_self_var_name}" is not presented in "{self.__class__.__name__}" class!'
                )
        return _dict

@dataclass
class WebdavData(DatabaseModel):
    employee_id: int = ... # type: ignore
    login: str = ... # type: ignore
    password: str = ... # type: ignore
    url: str = ... # type: ignore

@dataclass
class Subscription(DatabaseModel):
    employee_id: int = ... # type: ignore
    enabled: bool = ... # type: ignore
    notify_time: str = ... # type: ignore

@dataclass
class Shift(DatabaseModel):
    date: str = ... # type: ignore
    shift_type_id: int = ... # type: ignore
    employee_id: int = ... # type: ignore
    is_on_chat: bool = ... # type: ignore

@dataclass
class ShiftDate():
    _month_names = {
        "Январь": 1,
        "Февраль": 2,
        "Март": 3,
        "Апрель": 4,
        "Май": 5,
        "Июнь": 6,
        "Июль": 7,
        "Август": 8,
        "Сентябрь": 9,
        "Октябрь": 10,
        "Ноябрь": 11,
        "Декабрь": 12
    }

    year: int = ... # type: ignore
    month: Union[str, int] = ... # type: ignore
    day: int = ... # type: ignore

    def get_date(self):
        assert(self.year is not ...)
        assert(self.month is not ...)
        assert(self.day is not ...)
        if isinstance(self.month, str): 
            return datetime(
                year=self.year,
                month=self._month_names[self.month], # type: ignore
                day=self.day
            ).strftime('%Y-%m-%d')
        else:
            return datetime(
                year=self.year,
                month=self.month, # type: ignore
                day=self.day
            ).strftime('%Y-%m-%d')