import caldav
import datetime
from sm_bot.services.logger import logger

class Client:
    def __init__(self, login, password) -> None:
        webdav_url = 'https://webdav.fqrmix.ru'
        self.current_client = caldav.DAVClient(
            url=webdav_url,
            username=login,
            password=password
        )
        self.current_principle = self.current_client.principal()
        logger.info(f"[WebDAV] Connected by login: {login}")
        try:
            self.work_calendar = self.current_principle.calendar(name="Work")
            assert self.work_calendar
            self.work_calendar_url = self.work_calendar.url
            assert self.work_calendar_url
            logger.info(f"[WebDAV] Found Work calendar for login: {login}")
        except caldav.error.NotFoundError:
            logger.info(f"[WebDAV] Work calendar wasn't found for login: {login}. Creating calendar...")
            self.work_calendar = self.current_principle.make_calendar(name="Work")
            self.work_calendar_url = self.work_calendar.url
            assert self.work_calendar_url
            logger.info(f"[WebDAV] Work calendar was successfuly created for login: {login}")
            

    def get_calendars(self):
        calendars = self.current_principle.calendars()
        current_calendars = []
        current_calendar = {}
        if calendars:
            for c in calendars:
                current_calendar['name'] = c.name
                current_calendar['url'] = c.url
                current_calendars.append(current_calendar)
            return current_calendars
        else:
            return None

    def create_event(self, date_start, date_end, summary, month, time_start, time_end):
        try:
            event = self.work_calendar.save_event(
                dtstart=datetime.datetime(2022, month, date_start, time_start),
                dtend=datetime.datetime(2022, month, date_end, time_end),
                summary=summary
            )
        except Exception as error:
            logger.error(error, exc_info=True)

    def get_events(self, calendar_name):
        result = self.current_principle.calendar(name=calendar_name).events()
        if result == []:
            return None
        else:
            return result
    
    def delete_all_events(self, calendar_name):
        try:
            all_events = self.get_events(calendar_name=calendar_name)
            if all_events:
                for event in all_events:
                    event.delete()
            else:
                print('Calendar is empty!')
        except Exception as error:
            logger.error(error, exc_info=True)