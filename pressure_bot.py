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
import re

import telegramcalendar
from functional_bot import (
    select_data_from_postgresql,
    prepare_data_from_potgresql_to_graph,
    save_pressure_to_postgresql,
    arm_corrector,
    create_graph,
    )

from bot_settings import TOKEN, PROXY


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename="bot.log"
    )

ARM, PRESSURE, GRAPH_FOR_PERIOD, START, SET_TIMER = range(5)

arm_buttons = [["Right", "Left"]]
arms_markup = ReplyKeyboardMarkup(arm_buttons, one_time_keyboard=True)
markup_remove = ReplyKeyboardRemove(selective=False)


def start(update, context):
    """
    greet user, ask name of the arm for a new pressure data,
    save it into context
    """
    user_text = update.message
    text = (
        '''Hi, %s, I'm a pressure - keeper - bot.

        Which arm have you used?

        send /cancel to stop talking to me,
        or /set to set reminder'''
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
    ask user pressure data,
    save arm-input into context,
    close arm buttons
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
    take arm and pressure
    prepare pressure data like ['180', '90']
    take current datetime
    prepare and write new data to postgreSQL:
    username, systolic, diastolic, timestamp, date, arm
    Return calendar
    """
    user_input_arm = context.user_data['arm']
    arm = arm_corrector(user_input_arm)
    # TODO change format of saving arm-input

    user_input_pressure = update.message.text
    list_pressure = re.split(r'[\^\,\.:;\\/]', user_input_pressure)
    systolic, diastolic = list_pressure[0], list_pressure[1]
    date = datetime.datetime.now().date()
    timestamp = datetime.datetime.now()
    username = context.user_data['user_name']

    save_pressure_to_postgresql(
        username, systolic, diastolic, timestamp, date, arm
        )

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
    take current-user data from postgreSQL
    prepare data to graph
    return left arm and right arm graph.png for the choosen period

    """
    selected, date = telegramcalendar.process_calendar_selection(
        update, context
        )
    str_date = date.strftime("%d.%m.%Y")

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
        make_graph(update, context)

        return START


def make_graph(update, context):
    first_date = context.user_data.get('first_date')
    last_date = context.user_data.get('second_date')
    user = context.user_data['user_name']

    pressure_list = select_data_from_postgresql(first_date, last_date, user)

    arms = ["r", "l"]

    for arm in arms:
        try:
            arm_data = prepare_data_from_potgresql_to_graph(pressure_list, arm)

            graph = create_graph(arm_data)
            context.bot.send_document(
                chat_id=update.callback_query.message.chat_id,
                document=open(graph, 'rb')
            )

        except ValueError:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="There aren't any arm data per date"
                )
            return START

    if 'first_date' in context.user_data:
        del context.user_data['first_date']

    if 'second_date' in context.user_data:
        del context.user_data['second_date']


def take_time_for_timer(update, context):
    """
    take time from user and save it into context
    if it exists, add new value
    """
    text = "Enter time to reminder, like 21:14"
    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=markup_remove
        )

    return SET_TIMER


def alarm(context):
    """
    Send the alarm message
    """
    job = context.job
    context.bot.send_message(
        job.context, text="It's time to measure arterial pressure"
        )


def set_timer(update, context):
    """
    take alarm value from context
    find time now
    find differense between time now and alarm time
    and set timer.
    If it's more than one value, take differences between each other
    and set timers one by one
    """
    alarm_time = update.message.text
    context.user_data['alarm_time'] = datetime.datetime.strptime(alarm_time, "%H:%M").time()

    alarm_time = context.user_data['alarm_time']
    job = context.job_queue.run_daily(
        alarm, alarm_time, context=update.message.chat_id
        )
    context.chat_data['job'] = job
    update.message.reply_text('Timer successfully set!')

    return START


def cancel(update, context):
    """
    close the conversation,
    return START possition of the conversation handler
    """
    text = (
        "Bye! I hope we can talk again some day."
    )
    context.bot.send_message(chat_id=update.message.chat_id, text=text)

    return START


def main():
    updater = Updater(token=TOKEN, request_kwargs=PROXY, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ARM: [MessageHandler(Filters.regex('^(Right|Left)$'), arm)],

            PRESSURE: [MessageHandler(Filters.text, pressure)],

            GRAPH_FOR_PERIOD: [CallbackQueryHandler(inline_handler)],

            SET_TIMER: [MessageHandler(Filters.text, set_timer)],

            START: [CommandHandler('start', start)],

        },

        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('set', take_time_for_timer)
            ]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
