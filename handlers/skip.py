from buttons import start_markup
from states import States


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

    return States.START_BUTTON
