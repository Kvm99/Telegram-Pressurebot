from buttons import start_markup
from states import States

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

    return States.START_BUTTON
