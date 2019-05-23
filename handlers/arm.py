def arm(update, context):
    """
    ask user pressure data,
    save arm-input into context,
    close arm buttons
    """
    user_input_arm = update.message.text
    context.user_data['arm'] = user_input_arm
    text = (
        '''
        Ok, enter pressure data and pulse
        like 120/70 82 or
        systolic diastolic pulse
        '''
        )
    context.bot.send_message(
        chat_id=update.message.chat_id, text=text, reply_markup=markup_remove
        )

    return PRESSURE
