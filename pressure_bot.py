from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    )
import logging
import datetime
import psycopg2
import re
from collections import defaultdict

import telegramcalendar
from db_settings import config
from bot_settings import TOKEN, PROXY
from prepare_and_show_graph import (
    arm_corrector,
    get_date_and_time_now,
    take_value_from_user_json_version,
    prepare_data_to_json_writer,
    write_data_to_json_file,
    read_and_prepare_json_pressure_file_for_period,
    create_graph,
)

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename="bot.log"
    )

ARM, PRESSURE, GRAPH_FOR_PERIOD, START = range(4)

arm_buttons = [["Right", "Left"]]
period_buttons = [["All the time graph", "Graph for period", "Today graph", "Don't need a graph"]]

arms_markup = ReplyKeyboardMarkup(arm_buttons, one_time_keyboard=True)
period_markup = ReplyKeyboardMarkup(period_buttons, one_time_keyboard=True)
markup_remove = ReplyKeyboardRemove(selective=False)


def start(update, context):
    """
    greet user, ask arm for a new pressure data
    """
    user_text = update.message
    text = (
        '''Hi, %s, I'm a pressure - keeper - bot.
        Please enter on which arm your measured arterial pressure:
        Send /cancel to stop talking to me.'''
        % user_text['chat']['first_name']
        )
    user_name = user_text['chat']['username']
    context.user_data['user_name'] = user_name

    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=arms_markup
        )

    return ARM


def arm(update, context):
    """
    ask user pressure data, close arm buttons
    """
    user_input_arm = update.message.text
    context.user_data['arm'] = user_input_arm
    text = (
        "Ok, please enter your current pressure data: "
        )
    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=markup_remove
        )

    return PRESSURE


def pressure(update, context):
    """
    take arm and pressure from saved user data
    prepare pressure like ['180', '90']
    take currnet date and time and make them str-objects
    prepare and write new data (systolic, diastolic, date, time, arm) to json.
    Return calendar
    """
    user_input_arm = context.user_data['arm']
    arm = arm_corrector(user_input_arm)

    user_input_pressure = update.message.text
    list_pressure = re.split(r'[\^\,\.:;\\/]', user_input_pressure)
    systolic, diastolic = list_pressure[0], list_pressure[1]
    date = datetime.datetime.now().date()
    timestamp = datetime.datetime.now()
    username = context.user_data['user_name']

    save_pressure_to_postgresql(username, systolic, diastolic, timestamp, date, arm)

    text = (
        '''I see.
        If you'd like a graph, please choose period,
        if no, press /cancel'''
        )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=telegramcalendar.create_calendar()
        )

    return GRAPH_FOR_PERIOD


def inline_handler(update, context):
    """
    Take two dates from user input in calendar.
    send them to user,
    return left arm and right arm graphs for the choosen period

    """
    selected, date = telegramcalendar.process_calendar_selection(update, context)
    str_date = date.strftime("%d.%m.%Y")

    arms = ["r", "l"]

    if selected:
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="You selected %s" % str_date,
            reply_markup=markup_remove
            )

    if 'first_date' not in context.user_data:
        context.user_data['first_date'] = str_date

    elif 'second_date' not in context.user_data:
        context.user_data['second_date'] = str_date

        first_date = context.user_data['first_date']
        last_date = context.user_data['second_date']
        user = context.user_data['user_name']


    pressure_list = select_data_from_postgresql(first_date, last_date, user) 

    for arm in arms:
        arm_data = prepare_data_from_potgresql_to_graph(pressure_list, arm)
        print("arm_data", arm_data, "\n")
        graph = create_graph(arm_data)

        context.bot.send_document(
            chat_id=update.callback_query.message.chat_id,
            document=open(graph, 'rb')
        )


    if 'first_date' in context.user_data:
        del context.user_data['first_date']

    if 'second_date' in context.user_data:
        del context.user_data['second_date']

    return START


def select_data_from_postgresql(first_date, last_date, user):
    """
    select data for the user and time period
    """
    pressure_list = []
    date_generated = find_dates_in_period(first_date, last_date)
    connection = config()
    cursor = connection.cursor()

    for date in date_generated:
        date_format = datetime.datetime.strptime(date, "%Y-%m-%d").date()


        postgreSQL_select_query = """SELECT * FROM pressure WHERE username = %s and date = %s ;"""
        username = [user, date_format]
        cursor.execute(postgreSQL_select_query, username)

        pressure_data = cursor.fetchall()
        pressure_list.append(pressure_data)

    cursor.close()
    connection.close()

    return pressure_list


def prepare_data_from_potgresql_to_graph(pressure_list, arm):
    """
    find interval between 2 dates,
    read json file, make two lists for such dates:
    [systolic],[diastolic],[date_list], arm to graph.

    {"r": {"01.01.2000": {"10.00": [140,70]}},
    """
    pressure_list_for_arm = []   

    for date in pressure_list:
        day_arm_list = []

        for line in date:
            if line[-1] == arm:
                day_arm_list.append(line)
            else:
                continue
        pressure_list_for_arm.append(day_arm_list)

    systolic_list, diastolic_list, date_list = [], [], []

    if len(pressure_list_for_arm) == 1:
        for line in pressure_list_for_arm[0]:
            systolic, diastolic = line[2], line[3]
            time = datetime.datetime.strftime(line[4], "%H:%M")
            date_list.append(time)
            systolic_list.append(systolic)
            diastolic_list.append(diastolic)

        return systolic_list, diastolic_list, date_list, arm


    for day in pressure_list_for_arm:
        date = datetime.datetime.strftime(day[0][5], "%Y-%m-%d")

        if len(day) == 1:
            systolic, diastolic = day[0][2], day[0][3]
            date_list.append(date)
            systolic_list.append(systolic)
            diastolic_list.append(diastolic)

        if len(day) > 1:
            biggest_value = [0, 0]
            for line in day:
                systolic, diastolic = int(line[2]), int(line[3])

                if systolic > biggest_value[0]:
                    biggest_value = [systolic, diastolic]

                elif systolic == biggest_value[0]:
                    if diastolic > biggest_value[1]:
                        biggest_value = [systolic, diastolic]

                    else:
                        continue

                elif systolic < biggest_value[0]:
                    continue

            systolic, diastolic = str(biggest_value[0]), str(biggest_value[1])
            date_list.append(date)
            systolic_list.append(systolic)
            diastolic_list.append(diastolic)

    return systolic_list, diastolic_list, date_list, arm


def cancel(update, context):
    """
    close the conversation
    """
    text = (
        "Bye! I hope we can talk again some day."
    )
    context.bot.send_message(chat_id=update.message.chat_id, text=text)

    return START



def save_pressure_to_postgresql(username, systolic, diastolic, timestamp, date, arm):
    """
    save username(unique), arm, date, datetime, systolic, diastolic pressure
    """
    connection = config()
    cursor = connection.cursor()
    try:
        postgres_insert_users = """INSERT INTO users (username) VALUES (%s)"""
        record_to_users = username
        cursor.execute(postgres_insert_users, [record_to_users])
    except psycopg2.errors.UniqueViolation:
        print('there is an user un the DB')
        connection.rollback()

    finally:
        postgres_insert_pressure = """
        INSERT INTO pressure (username, systolic, diastolic, timestamp, date, arm)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        records_to_pressure = (
            username,
            systolic,
            diastolic,
            timestamp,
            date,
            arm
            )

        cursor.execute(postgres_insert_pressure, records_to_pressure)
        cursor.close()
        connection.commit()
        connection.close()


def find_dates_in_period(first_date, last_date):
    start_date = datetime.datetime.strptime(first_date, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(last_date, "%d.%m.%Y")
    end= end_date + datetime.timedelta(days=1)

    date_generated = [
        (start_date + datetime.timedelta(days=x)).strftime("%Y-%m-%d")
        for x in range(0, (end-start_date).days)
        ]
    return date_generated


def select_data_from_postgresql_1(first_date, last_date, user):
    """
    select data for the user and time period
    """
    pressure_list = []
    date_generated = find_dates_in_period(first_date, last_date)
    connection = config()
    cursor = connection.cursor()
    postgreSQL_select_query = """SELECT * FROM pressure WHERE username = %s;"""
    username = user
    cursor.execute(postgreSQL_select_query, [username])

    pressure_data = cursor.fetchall()
    cursor.close()
    connection.close()

    for line in pressure_data:

        for date in date_generated:
            date_format = datetime.datetime.strptime(date, "%Y-%m-%d").date()

            if date_format == line[5]:
               pressure_list.append(line)
    return pressure_list  


def main():
    updater = Updater(token=TOKEN, request_kwargs=PROXY, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ARM: [MessageHandler(Filters.regex('^(Right|Left)$'), arm)],

            PRESSURE: [MessageHandler(Filters.text, pressure)],

            GRAPH_FOR_PERIOD: [CallbackQueryHandler(inline_handler)],

            START: [CommandHandler('start', start)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
