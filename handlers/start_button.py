from helpers.timers import show_timers
from buttons import arms_markup, markup_remove
from states import States
import telegramcalendar


def start_button(update, context):
    user_input = update.message.text

    if user_input == "ADD PRESSURE":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Which arm have you used?",
            reply_markup=arms_markup
            )
        return States.ARM

    elif user_input == "SET TIMER":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Enter time to reminder, like 21:14",
            reply_markup=markup_remove
            )
        return States.SET_TIMER

    elif user_input == "REMOVE TIMER":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Which timer you'd like to stop? Enter like 20:18",
            reply_markup=markup_remove
            )
        return States.REMOVE_TIMER

    elif user_input == "SHOW TIMERS":
        return show_timers(update, context)

    elif user_input == "SHOW GRAPHS":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Choose period for graphs",
            reply_markup=telegramcalendar.create_calendar()
            )
        return States.GRAPH_FOR_PERIOD

    elif user_input == "Add or change personal data to better analytics":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Enter your AGE:",
            reply_markup=markup_remove
            )
        return States.AGE

    else:
        raise NameError('Incorrect input')
