import matplotlib.pyplot as plot
from matplotlib.pyplot import savefig
import datetime
import io

from states import States
from buttons import start_markup
from helpers.save_select_from_postgresql import select_data_from_postgresql
from helpers.prepare_data import (
    make_list_for_arm,
    prepare_data_for_one_day,
    prepare_data_for_many_days
)


def if_dates_consecutive(first_date, last_date):
    datetime_first_date = datetime.datetime.strptime(first_date, "%Y-%m-%d")
    datetime_last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")

    if datetime_last_date >= datetime_first_date:
        return True


def prepare_data_from_potgresql_to_graph(pressure_list, arm):
    """
    if it's only one-day data, make graph with time-indexes,
    if there are a lot of days and pressure-records,
    find the biggest value per each day.
    return: [systolic],[diastolic],[date_list], arm
    """
    pressure_list_new = make_list_for_arm(pressure_list, arm)

    if len(pressure_list_new) == 0:
        raise ValueError("There aren't any data per date")

    elif len(pressure_list_new) == 1:
        return prepare_data_for_one_day(pressure_list_new, arm)

    elif len(pressure_list_new) > 1:
        return prepare_data_for_many_days(pressure_list_new, arm)


def create_graph(arm_list):
    """
    take [systolic_pressure], [diastolic_pressure], [dates or time], arm

    and makes graph, save it like r_graph.png or l_graph.png
    """
    plot.close("all")
    figsize = (8, 4)
    plot.style.use('seaborn-dark')
    fig = plot.figure(figsize=figsize, facecolor='pink', frameon=True)

    ax = fig.add_subplot(111)

    arm, list_systolic_pressure, list_diastolic_pressure = \
        marking_on_coordinate_axes(arm_list)

    plot.title('%s arm graph' % arm)
    dates = arm_list[2]
    ax.set_xticklabels(dates, rotation=10)
    ax.plot(dates, list_systolic_pressure)
    ax.plot(dates, list_diastolic_pressure)

    for ax in fig.axes:
        ax.grid(True)

    graph_name = '%s_graph.png' % arm
    graph_io = io.BytesIO()
    graph_io.name = graph_name
    savefig(graph_io, format='png')
    graph_io.seek(0)
    return graph_io


def marking_on_coordinate_axes(arm_list):
    """
    Take arm list and makes systolic and diastolic lists
    for marking on coordinate axes
    """
    arm = arm_list[3]

    if arm != 'Right' and arm != 'Left':
        raise ValueError("Incorrect arm name")

    list_systolic_pressure = list(map(int, arm_list[0]))
    list_diastolic_pressure = list(map(int, arm_list[1]))

    return arm, list_systolic_pressure, list_diastolic_pressure


def make_graph(update, context):
    """
    take data form postgresql,
    find correct information for requested dates,
    makes graphs.
    Delete requested dates from context
    """
    first_date = context.user_data.get('first_date')
    last_date = context.user_data.get('second_date')
    user = context.user_data.get('user_name')

    end_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")
    end = end_date + datetime.timedelta(days=1)
    str_end_date = end.strftime("%Y-%m-%d")

    if if_dates_consecutive(first_date, last_date) is True:
        pressure_data = select_data_from_postgresql(
            user, first_date,
            str_end_date
        )

    else:
        context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="Sequence of days is broken",
                reply_markup=start_markup
                )
        return States.START_BUTTON

    arms = ["Left", "Right"]

    for arm in arms:
        try:
            arm_data = prepare_data_from_potgresql_to_graph(pressure_data, arm)
            print(arm_data)
            graph_io = create_graph(arm_data)
            context.bot.send_document(
                chat_id=update.callback_query.message.chat_id,
                document=graph_io
            )

        except ValueError:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="There aren't any %s arm data per dates" % arm,
                reply_markup=start_markup
                )
    return States.START_BUTTON
