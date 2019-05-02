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
    save_user_to_postgresql,
    save_pressure_to_postgresql,
    arm_corrector,
    create_graph,
    select_data_picked_by_dates,
    find_dates_in_period,
    analysis_result
    )

from bot_settings import TOKEN, PROXY


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename="bot.log"
    )

START, AGE, SEX, WEIGHT, ADD_PRESSURE, ARM, PRESSURE, GRAPH_FOR_PERIOD, \
    SET_TIMER, REMOVE_TIMER, START_BUTTON, SHOW_TIMERS = range(12)

start_button = [
    ["ADD PRESSURE", "SHOW GRAPHS"],
    ["SET TIMER", "REMOVE TIMER", "SHOW TIMERS"],
    ["Add or change personal data to better analytics"]
    ]
start_markup = ReplyKeyboardMarkup(start_button, one_time_keyboard=True)
sex_buttons = [["male", "female", "other"]]
sex_markup = ReplyKeyboardMarkup(sex_buttons, one_time_keyboard=True)
arm_buttons = [["Right", "Left"]]
arms_markup = ReplyKeyboardMarkup(arm_buttons, one_time_keyboard=True)
work_buttons = [["Active", "Sitting", "Combine"]]
work_markup = ReplyKeyboardMarkup(work_buttons, one_time_keyboard=True)
markup_remove = ReplyKeyboardRemove(selective=False)


def greeting(update, context):
    """
    start with age input
    """
    print(context.user_data)
    user_text = update.message
    text = (
        '''
        Hi, %s, I'm a PressureKeeperBot.

        For better analytics please enter
        YOUR AGE:

        send /cancel to stop talking to me
        or /skip to go to menu.
        '''
        % user_text['chat']['first_name']
        )

    user_name = user_text['chat']['username']
    context.user_data['user_name'] = user_name

    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=markup_remove
        )

    return AGE


def age(update, context):
    """
    save age into context.user_data,
    ask sex
    """
    user_input = update.message.text
    context.user_data['age'] = user_input
    # TODO modify age every year

    text = "Choose your sex:"

    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=sex_markup
        )

    return SEX


def sex(update, context):
    """
    save sex into context.user_data,
    ask weight
    """
    user_input = update.message.text
    context.user_data['sex'] = user_input

    text = "Also enter your weight:"
    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=markup_remove
        )

    return WEIGHT


def weight(update, context):
    """
    save weight into context.user_data,
    ask work
    """
    user_input = update.message.text
    context.user_data['weight'] = user_input

    text = "Choose nature of your work"

    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=work_markup
        )

    return ADD_PRESSURE


def add_pressure(update, context):
    """
    save work into context.user_data,
    save all user data into Postgresql
    ask name of the arm for a new pressure data,
    save it into context
    """
    user_input = update.message.text
    context.user_data['work'] = user_input

    username = context.user_data['user_name']
    sex = context.user_data['sex']
    age = context.user_data['age']
    weight = context.user_data['weight']
    work = context.user_data['work']

    save_user_to_postgresql(username, sex, age, weight, work)

    text = (
        '''
        Let's save your pressure data.

        Which arm have you used?

        '''
        )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=arms_markup
        )

    return ARM


def start_button(update, context):
    user_input = update.message.text

    if user_input == "ADD PRESSURE":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Which arm have you used?",
            reply_markup=arms_markup
            )
        return ARM

    elif user_input == "SET TIMER":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Enter time to reminder, like 21:14",
            reply_markup=markup_remove
            )
        return SET_TIMER

    elif user_input == "REMOVE TIMER":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Which timer you'd like to stop? Enter like 20:18",
            reply_markup=markup_remove
            )
        return REMOVE_TIMER

    elif user_input == "SHOW TIMERS":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Press any button to continue",
            reply_markup=markup_remove
            )  # TODO make without any input from user
        return SHOW_TIMERS

    elif user_input == "SHOW GRAPHS":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Choose period for graphs",
            reply_markup=telegramcalendar.create_calendar()
            )  # TODO make without any input from user
        return GRAPH_FOR_PERIOD

    elif user_input == "Add or change personal data to better analytics":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Enter your AGE:",
            reply_markup=markup_remove
            )
        return AGE

    else:
        print('Incorrect input', user_input)
        raise NameError('Incorrect input')


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
    username = context.user_data.get('user_name')

    save_pressure_to_postgresql(
        username, systolic, diastolic, timestamp, date, arm
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

    return START_BUTTON


def graph_for_period(update, context):
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

        text = "What you'd like to do next?"

        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=text,
            reply_markup=start_markup)

        return START_BUTTON


def make_graph(update, context):
    """
    take data form postgresql,
    find correct information for requested dates,
    makes graphs.
    Delete requested dates from context
    """
    first_date = context.user_data.get('first_date')
    last_date = context.user_data.get('second_date')
    user = context.user_data.get('user_name')

    pressure_data = select_data_from_postgresql(user)
    try:
        date_generated = find_dates_in_period(first_date, last_date)
    except NameError:
        context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="Sequence of days is broken",
                reply_markup=start_markup
                )
        return START_BUTTON

    pressure_list = select_data_picked_by_dates(pressure_data, date_generated)

    arms = ["l", "r"]

    try:  # TODO it falls if l-arm data is empty. Shouldn't
        for arm in arms:
            arm_data = prepare_data_from_potgresql_to_graph(pressure_list, arm)

            graph = create_graph(arm_data)
            context.bot.send_document(
                chat_id=update.callback_query.message.chat_id,
                document=open(graph, 'rb')
            )

    except ValueError:
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="There aren't any arm data per date",
            reply_markup=start_markup
            )
        return START_BUTTON

    if 'first_date' in context.user_data:
        del context.user_data['first_date']

    if 'second_date' in context.user_data:
        del context.user_data['second_date']


def take_time_for_timer(update, context):
    """
    take time from user and save it into context
    if it exists, add new value
    """
    text = "Enter time to daily reminder, like 21:14"
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
        job.context, text="IT'S TIME to measure arterial pressure"
        )

    return START_BUTTON


def set_timer(update, context):
    """
    take new value for timer,
    added it into context.user_data like ['alarm_time'] = ['21:14'],
    make job for timer, put it into chat_data like chat_data['21:14'] = job
    """
    new_timer = update.message.text
    timer = datetime.datetime.strptime(new_timer, "%H:%M").time()
    timer_list = []

    if 'alarm_time' in context.user_data:
        timer_list = context.user_data['alarm_time']
        timer_list.append(timer)

    else:
        context.user_data['alarm_time'] = timer_list
        timer_list.append(timer)

    job = context.job_queue.run_daily(
        alarm, timer, context=update.message.chat_id
        )
    context.chat_data[new_timer] = job

    update.message.reply_text(
        'Timer successfully set!',
        reply_markup=start_markup
        )

    return START_BUTTON


def remove_timer(update, context):
    """
    remove timer in the job queue,
    if it's not exist, sent message
    """
    existed_timer = update.message.text

    try:
        timer = datetime.datetime.strptime(existed_timer, "%H:%M").time()

    except ValueError:
        update.message.reply_text(
            "Please enter like 21:34",
            reply_markup=start_markup)

    timer_list = context.user_data.get('alarm_time')

    if timer_list is not None and timer in timer_list:
        job = context.chat_data.get(existed_timer)

        job.schedule_removal()
        timer_list.remove(timer)

        update.message.reply_text(
            "Timer successfully stoped",
            reply_markup=start_markup
            )
    # elif user would like to delete all the timers
    # context.job_queue.stop()

    else:
        update.message.reply_text(
            "There isn't such timer",
            reply_markup=start_markup
            )

    return START_BUTTON


def show_timers(update, context):
    """
    show all existed timers
    """
    timers = context.user_data.get('alarm_time')
    if timers is not None:
        text = ""
        for time in timers:
            text += "%s \n" % time

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
            reply_markup=start_markup
            )

    else:
        print('2')
        text = "There aren't any timers"
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
            reply_markup=start_markup
            )

    return START_BUTTON


def cancel(update, context):
    """
    close the conversation,
    return START possition of the conversation handler
    """
    text = (
        "Bye! I hope we can talk again some day."
    )
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=start_markup)

    return START_BUTTON


def skip(update, context):
    """
    close the conversation,
    return START possition of the conversation handler
    """
    text = "Ok, you could do it later"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=start_markup
        )

    return START_BUTTON


def main():
    updater = Updater(token=TOKEN, request_kwargs=PROXY, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', greeting)],

        states={

            START: [CommandHandler('start', greeting)],

            AGE: [MessageHandler(Filters.text, age)],

            SEX: [MessageHandler(Filters.text, sex)],

            WEIGHT: [MessageHandler(Filters.text, weight)],

            ADD_PRESSURE: [MessageHandler(Filters.text, add_pressure)],

            ARM: [MessageHandler(Filters.regex('^(Right|Left)$'), arm)],

            PRESSURE: [MessageHandler(Filters.text, pressure)],

            GRAPH_FOR_PERIOD: [CallbackQueryHandler(graph_for_period)],

            SET_TIMER: [MessageHandler(Filters.text, set_timer)],

            REMOVE_TIMER: [MessageHandler(Filters.text, remove_timer)],

            SHOW_TIMERS: [MessageHandler(Filters.text, show_timers)],

            START_BUTTON: [MessageHandler(Filters.text, start_button)]

        },

        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('skip', skip)
            ]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
