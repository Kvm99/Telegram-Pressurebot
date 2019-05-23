from buttons import sex_markup
from states import States


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

    return States.SEX
