def add_pressure(update, context):
    """
    save work into context.user_data,
    save all user data into Postgresql
    ask name of the arm for a new pressure data,
    save it into context
    """
    user_input = update.message.text
    context.user_data['work'] = user_input

    username = context.user_data['user_name']
    sex = context.user_data['sex']
    age = context.user_data['age']
    weight = context.user_data['weight']
    work = context.user_data['work']

    save_user_to_postgresql(username, sex, age, weight, work)

    text = (
        '''
        Let's save your pressure data.

        Which arm have you used?

        send /skip to go to menu

        '''
        )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=arms_markup
        )

    return ARM
