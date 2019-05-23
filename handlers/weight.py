from buttons import work_markup
from states import States

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

    return States.ADD_PRESSURE
