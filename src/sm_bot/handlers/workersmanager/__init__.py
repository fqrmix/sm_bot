import uuid
import datetime
from sm_bot.config import config
from sm_bot.services.logger import logger, trace_logger
from sm_bot.handlers.workersmanager.day_workers import DayWorkers

# Updating CSV file
def update_actual_csv(nextpath, path):
    '''
        Function that update actual CSV file with CSV file for next month
        _______
        Arguments:
            *nextpath == Path to CSV file for next month
            *path == Path to actual CSV file
    '''
    try:
        with open(path, 'w+', encoding='utf-8') as write_file:
            with open(nextpath, 'r', encoding='utf-8') as read_file:
                data = read_file.read()
                write_file.write(data)
            logger.info("[load] The schedule for next month has been successfully updated!")
    except Exception as error_msg:
        logger.error(error_msg, exc_info=True)

###########################
## Initialization block ###
###########################

logger_data = {
    'trace_id': uuid.uuid4()
}

current_date = datetime.date.today()
if current_date.day == 1:
    trace_logger.info('[main] Time to new CSV...\nUpdating', extra=logger_data)
    update_actual_csv(config.NEXT_MONTH_CSV_PATH, config.CSV_PATH) # Update actual CSV file
    trace_logger.info('[main] CSV file was successfully loaded! Strarting polling!', extra=logger_data)
else:
    trace_logger.info("[main] New CSV doesn't needed! Starting polling!", extra=logger_data)

today_workers = DayWorkers()

