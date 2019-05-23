def sex(update, context):
    """
    save sex into context.user_data,
    ask weight
    """
    user_input = update.message.text
    context.user_data['sex'] = user_input

    text = "Also enter your weight:"
    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=markup_remove
        )

    return WEIGHT
