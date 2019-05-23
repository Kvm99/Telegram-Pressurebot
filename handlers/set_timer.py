import datetime
from buttons import start_markup
from states import States
from helpers.timers import alarm


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
        timer_list = context.user_data.get('alarm_time')
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

    return States.START_BUTTON
