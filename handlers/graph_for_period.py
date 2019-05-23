def graph_for_period(update, context):
    """
    Take two dates from user input in calendar.
    send them to user,
    take current-user data from postgreSQL
    prepare data to graph
    return left arm and right arm graph.png for the choosen period

    """
    selected, date = telegramcalendar.process_calendar_selection(
        update, context
        )
    str_date = date.strftime("%Y-%m-%d")

    if selected:
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="You selected %s" % str_date,
            reply_markup=markup_remove
            )

    if 'first_date' not in context.user_data:
        context.user_data['first_date'] = str_date

    elif 'second_date' not in context.user_data:
        context.user_data['second_date'] = str_date
        make_graph(update, context)

        text = "What you'd like to do next?"

        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=text,
            reply_markup=start_markup)

        if 'first_date' in context.user_data:
            del context.user_data['first_date']

        if 'second_date' in context.user_data:
            del context.user_data['second_date']

        return START_BUTTON
