import re
import datetime
from helpers.save_select_from_postgresql import save_pressure_to_postgresql
from helpers.analytics import analysis_result
from buttons import start_markup
from states import States


def pressure(update, context):
    """
    take arm and pressure
    prepare pressure data like ['180', '90']
    take current datetime
    prepare and write new data to postgreSQL:
    username, systolic, diastolic, timestamp, date, arm
    Return calendar
    """
    arm = context.user_data.get('arm')
    username = context.user_data.get('user_name')
    user_input_pressure = update.message.text

    timestamp = datetime.datetime.now()
    list_pressure = re.split(r'[\^\,\.:;\\/\s]', user_input_pressure)

    try:
        systolic = list_pressure[0]
        diastolic = list_pressure[1]
        pulse = list_pressure[2]
        save_pressure_to_postgresql(
            username, systolic, diastolic, timestamp, arm, pulse
            )
    except (ValueError, IndexError):
        systolic, diastolic = list_pressure[0], list_pressure[1]
        save_pressure_to_postgresql(
            username, systolic, diastolic, timestamp, arm
            )

    analytics = analysis_result(systolic, diastolic)

    text = (
        '''
        New pressure data added. \n
        %s
        ''' % analytics
        )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=start_markup
        )

    return States.START_BUTTON
