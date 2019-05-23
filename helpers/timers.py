from buttons import start_markup
from states import States

def alarm(context):
    """
    Send the alarm message
    """
    job = context.job
    context.bot.send_message(
        job.context, text="IT'S TIME to measure arterial pressure"
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
        text = "There aren't any timers"
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
            reply_markup=start_markup
            )

    return States.START_BUTTON


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