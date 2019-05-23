import datetime
from buttons import start_markup
from states import States


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

    return States.START_BUTTON
