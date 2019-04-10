import datetime
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
import re
import telegramcalendar

from bot_settings import TOKEN, PROXY
from prepare_and_show_graph import (
    arm_corrector,
    get_date_and_time_now,
    take_value_from_user_json_version,
    prepare_data_to_json_writer,
    write_data_to_json_file,
    read_and_prepare_json_pressure_file,
    read_and_prepare_json_pressure_file_for_period,
    read_and_prepare_json_pressure_file_per_day,
    create_graph,
)

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename="bot.log"
    )

ARM, PRESSURE, GRAPH, GRAPH_FOR_PERIOD, START = range(5)

arm_buttons = [["Right", "Left"]]
period_buttons = [["All the time graph", "Graph for period", "Today graph", "Don't need a graph"]]

arms_markup = ReplyKeyboardMarkup(arm_buttons, one_time_keyboard=True)
period_markup = ReplyKeyboardMarkup(period_buttons, one_time_keyboard=True)
markup_remove = ReplyKeyboardRemove(selective=False)


def start(update, context):
    user_text = update.message
    text = (
        '''Hi, %s, I'm a pressure - keeper - bot.
        Please enter on which arm your measured arterial pressure:
        Send /cancel to stop talking to me.'''
        % user_text['chat']['first_name']
        )

    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=arms_markup
        )

    return ARM


def arm(update, context):
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
    user_input_arm = context.user_data['arm']
    arm = arm_corrector(user_input_arm)

    user_input_pressure = update.message.text
    list_pressure = re.split(r'[\^\,\.:;\\/]', user_input_pressure)

    date_and_time = get_date_and_time_now()
    pressure_and_date = take_value_from_user_json_version(list_pressure, date_and_time)

    new_pressure_data = prepare_data_to_json_writer(pressure_and_date, arm)
    write_data_to_json_file(new_pressure_data)

    text = (
        '''I see.
        You'd like pressure graph for all the time or only for today?'''
        )
    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=period_markup
        )

    return GRAPH


def graph(update, context):
    user_choice = update.message.text

    if user_choice == "Don't need a graph":
        text = (
            '''Ok. New pressure data added.
            BYE!'''
            )

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return START

    elif user_choice == "All the time graph":
        right_arm_data = read_and_prepare_json_pressure_file('r')
        left_arm_data = read_and_prepare_json_pressure_file('l')
        create_graph(right_arm_data)
        create_graph(left_arm_data)

        context.bot.send_document(
            chat_id=update.message.chat_id, document=open('r_graph.png', 'rb')
            )
        context.bot.send_document(
            chat_id=update.message.chat_id, document=open('l_graph.png', 'rb')
            )
        return START

    elif user_choice == "Graph for period":
        context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Please select a date: ",
        reply_markup=telegramcalendar.create_calendar()
        )
        return GRAPH_FOR_PERIOD
        
    elif user_choice == 'Today graph':
        date = datetime.datetime.now().date()
        str_date = date.strftime("%d.%m.%Y")

        right_arm_data = read_and_prepare_json_pressure_file_per_day('r', str_date)
        left_arm_data = read_and_prepare_json_pressure_file_per_day('l', str_date)
        create_graph(right_arm_data)
        create_graph(left_arm_data)

        context.bot.send_document(
            chat_id=update.message.chat_id, document=open('r_graph.png', 'rb')
            )
        context.bot.send_document(
            chat_id=update.message.chat_id, document=open('l_graph.png', 'rb')
            )
        return START


def inline_handler(update, context):

    selected, date = telegramcalendar.process_calendar_selection(update, context)
    str_date = date.strftime("%d.%m.%Y")

    if selected:
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="You selected %s" %str_date,
            reply_markup=markup_remove
            )

    if 'first_date' not in context.user_data:
        context.user_data['first_date'] = str_date
    elif 'second_date' not in context.user_data:
        context.user_data['second_date'] = str_date

        first_date = context.user_data['first_date']
        last_date = context.user_data['second_date']

        arms = ['r', 'l']
        for arm in arms:
            arm_data = read_and_prepare_json_pressure_file_for_period(arm, first_date, last_date)
            create_graph(arm_data)

        #right_arm_data = read_and_prepare_json_pressure_file_for_period('r', first_date, last_date)
        #left_arm_data = read_and_prepare_json_pressure_file_for_period('l', first_date, last_date)
        #create_graph(right_arm_data)
        #create_graph(left_arm_data)

        context.bot.send_document(
            chat_id=update.callback_query.message.chat_id, document=open('r_graph.png', 'rb')
            )
        context.bot.send_document(
            chat_id=update.callback_query.message.chat_id, document=open('l_graph.png', 'rb')
            )

        if 'first_date' in context.user_data: del context.user_data['first_date']
        if 'second_date' in context.user_data: del context.user_data['second_date']

        return START


def cancel(update, context):
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

            GRAPH: [MessageHandler(Filters.text, graph)],

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
