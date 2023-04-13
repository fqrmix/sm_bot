from datetime import datetime
from .gateway import DatabaseGateway
from .models import DatabaseModel
from typing import (List, Tuple, Union, Dict)
from dataclasses import dataclass

class DatabaseFacade:
    def __init__(self) -> None:
        self.database_gateway = DatabaseGateway()

    def get_day_chatters(self, date: datetime) -> Union[DatabaseModel, None]:
        sql_query = \
        f"""
        SELECT
            s.date as shift_date,
            emp.name as employee_name,
            dep.name as department_name, 
            s.is_on_chat
        FROM shift s

        INNER JOIN employee emp
            ON s.employee_id = emp.id
        INNER JOIN department dep
            ON emp.department_id = dep.id
        INNER JOIN shift_type st
            ON s.shift_type_id=st.id

        WHERE s.date='{date.strftime('%Y-%m-%d')}' AND s.is_on_chat = TRUE
        ORDER BY dep.name DESC, st.start_time;
        """
        self.database_gateway.open_connection()
        result = self.database_gateway.execute_query(query=sql_query)
        self.database_gateway.close_connection()
        if result:
            print(result.get_dict())

    def get_day_workers(self, date: datetime) -> Union[DatabaseModel, None]:
        sql_query = \
        f"""
        SELECT
            s.date as shift_date,
            emp.name as employee_name,
            dep.name as department_name,
            st.start_time as shift_start,
            st.end_time as shift_end
        FROM shift s

        INNER JOIN employee emp
            ON s.employee_id = emp.id
        INNER JOIN department dep
            ON emp.department_id = dep.id
        INNER JOIN shift_type st
            ON s.shift_type_id=st.id

        WHERE date = '{date.strftime('%Y-%m-%d')}'
        ORDER BY dep.name DESC, st.start_time;
        """
        self.database_gateway.open_connection()
        result = self.database_gateway.execute_query(query=sql_query)
        self.database_gateway.close_connection()
        if result:
            return result.get_dict()

    # def get_day_workers(self) -> Union[List[Dict], None]:
    #     ...
