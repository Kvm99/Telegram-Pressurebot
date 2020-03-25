from buttons import markup_remove
from states import States


def greeting(update, context):
    """
    greeting and ask for age input
    """
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

    return States.AGE
