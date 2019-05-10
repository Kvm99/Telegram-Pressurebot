import datetime
import psycopg2
import matplotlib.pyplot as plot
import os
from matplotlib.pyplot import savefig
from db_settings import config


def make_list_for_arm(pressure_list, arm):
    """
    from pressure_list makes list for "Left" or "Right" arm,
    then prepare them like list with lists (one per date)
    """
    arm_list = [line for line in pressure_list if line[-2] == arm]

    pressure_list_new = []
    comparison_date = datetime.date(1, 1, 1)
    new_list = []

    for line in arm_list:
        date = line[4].date()

        if date > comparison_date:
            new_list = []
            new_list.append(line)
            pressure_list_new.append(new_list)
            comparison_date = date
        else:
            new_list.append(line)
    print(pressure_list_new)
    return pressure_list_new


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



def prepare_data_for_one_day(pressure_list_new, arm):
    """
    if there are only one day data in pressure list,
    take first and only one list from pressure_list_new
    and makes lists systolic_list, diastolic_list, date_list, arm
    """
    systolic_list, diastolic_list, date_list = [], [], []

    for each_time in pressure_list_new[0]:
            systolic, diastolic = each_time[2], each_time[3]
            time = datetime.datetime.strftime(each_time[4], "%H:%M")

            systolic_list, diastolic_list, date_list = append_to_lists(
                systolic_list, diastolic_list,
                date_list, systolic, diastolic, time
                )

    return systolic_list, diastolic_list, date_list, arm


def prepare_data_for_many_days(pressure_list_new, arm):
    """
    if there are a lot of day's data in list,
    take one by one and makes lists:
    systolic_list, diastolic_list, date_list, arm.
    When there are a lot of values in a day, 
    find biggest one
    """
    systolic_list, diastolic_list, date_list = [], [], []

    for day in pressure_list_new:
        date = datetime.datetime.strftime(day[0][4], "%Y-%m-%d")

        if len(day) == 1:
            systolic, diastolic = day[0][2], day[0][3]

            systolic_list, diastolic_list, date_list = append_to_lists(
                systolic_list, diastolic_list,
                date_list, systolic, diastolic, date
                )

        if len(day) > 1:
            systolic, diastolic = find_biggest_value_per_day(day)

            systolic_list, diastolic_list, date_list = append_to_lists(
                systolic_list, diastolic_list,
                date_list, systolic, diastolic, date
                )

    return systolic_list, diastolic_list, date_list, arm


def append_to_lists(
    systolic_list, diastolic_list, date_list,
    systolic, diastolic, date
    ):
    """
    Append systolic, diastolic, date to similar lists
    """
    systolic_list.append(systolic)
    diastolic_list.append(diastolic)
    date_list.append(date)

    return systolic_list, diastolic_list, date_list


def find_biggest_value_per_day(day_data):
    # TODO make less inclusion
    """
    Take pressure data per day and find
    biggest value.
    If some systolic and other systolic equal,
    compare by diastolic
    """
    biggest_value = [0, 0]
    for line in day_data:
        systolic, diastolic = int(line[2]), int(line[3])

        if systolic > biggest_value[0]:
            biggest_value = [systolic, diastolic]

        elif systolic == biggest_value[0]:
            if diastolic > biggest_value[1]:
                biggest_value = [systolic, diastolic]

            else:
                continue

        elif systolic < biggest_value[0]:
            continue

    systolic, diastolic = str(biggest_value[0]), str(biggest_value[1])

    return systolic, diastolic


def save_pressure_to_postgresql(
        username, systolic, diastolic, timestamp, arm, pulse=None
        ):
    """
    save username(unique), systolic, diastolic, timestamp, date, arm
    """
    connection = config()
    cursor = connection.cursor()
    try:
        postgres_insert_users = """INSERT INTO users (username) VALUES (%s)"""
        record_to_users = username
        cursor.execute(postgres_insert_users, [record_to_users])
    except psycopg2.errors.UniqueViolation:
        connection.rollback()

    finally:
        postgres_insert_pressure = """
        INSERT INTO pressure (
            username, systolic, diastolic, timestamp, arm, pulse
            )
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        records_to_pressure = (
            username,
            systolic,
            diastolic,
            timestamp,
            arm,
            pulse
            )

        cursor.execute(postgres_insert_pressure, records_to_pressure)
        cursor.close()
        connection.commit()
        connection.close()


def save_user_to_postgresql(
        user_name, sex, age, weight, work
        ):
    """
    save user data to postgresql
    """
    connection = config()
    cursor = connection.cursor()
    try:
        postgres_insert_users = """
        INSERT INTO users
        (username, sex, age, weight, work)
        VALUES (%s, %s, %s, %s, %s)"""
        records_to_users = (
            user_name,
            sex,
            age,
            weight,
            work
            )
        cursor.execute(postgres_insert_users, records_to_users)

    except psycopg2.errors.UniqueViolation:
        connection.rollback()

        postgres_insert_users = """
        UPDATE users SET
        sex=%s, age=%s, weight=%s, work=%s WHERE username=%s
        """
        records_to_users = (sex, age, weight, work, user_name)
        cursor.execute(postgres_insert_users, records_to_users)

    finally:
        cursor.close()
        connection.commit()
        connection.close()


def select_data_from_postgresql(user, first_date, last_date):
    """
    select data for the user and time period
    """
    connection = config()
    cursor = connection.cursor()
    postgreSQL_select_query = """
            SELECT * FROM pressure WHERE username = %s
            AND timestamp >= %s AND timestamp <= %s;
        """
    details = [user, first_date, last_date]
    cursor.execute(postgreSQL_select_query, details)

    pressure_data = cursor.fetchall()
    cursor.close()
    connection.close()

    return pressure_data  # TODO make structure unchangeable


def if_dates_consecutive(first_date, last_date):
    datetime_first_date = datetime.datetime.strptime(first_date, "%Y-%m-%d")
    datetime_last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")

    if datetime_last_date >= datetime_first_date:
        return True


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

    directory = os.path.dirname(os.path.abspath(__file__))
    graph_name = os.path.join(directory, '%s_graph.png' % arm)
    savefig(graph_name)

    return '%s_graph.png' % arm


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


def analysis_pressure_value(systolic, diastolic):
    """
    take systolic and diastolic and makes recomendation
    based on values
    """
    systolic, diastolic = int(systolic), int(diastolic)

    if systolic > 100 and systolic < 140:
        return "Good"

    elif systolic >= 140 and systolic <= 150:
        return '''
            Not good.
            You'd better lay down and take medecine
            '''

    elif systolic > 150:
        return '''
            Dangerous!
            Call 911 or 112 in Russia. Lay down and take medecine
            '''

    elif systolic <= 100:
        return '''
            Not good.
            What about a cup of strong tea or coffee?
            '''


def analysis_pressure_difference(systolic, diastolic):
    """
    take systolic and diastolic values
    find difference between them and make recomendations
    """

    systolic, diastolic = int(systolic), int(diastolic)
    difference = systolic - diastolic

    if difference < 50:
        return "Good"

    elif difference >= 50:
        text = ('''
            You shold go to cardiologist,
            because your difference between systolic
            and diastolic pressure is dangerous
            ''')
        return text


def analysis_result(systolic, diastolic):
    # TODO make less inclusion
    """
    prepare result of analytic to bot
    """
    value_analys = analysis_pressure_value(systolic, diastolic)
    difference_analys = analysis_pressure_difference(systolic, diastolic)

    if value_analys == "Good" and difference_analys == "Good":
        return "Great values!"

    elif value_analys == "Good" and difference_analys != "Good":
        return difference_analys

    elif difference_analys == "Good" and value_analys != "Good":
        return value_analys

    elif value_analys != "Good" and difference_analys != "Good":
        text = "%s  %s" % (value_analys, difference_analys)
        return text


def main():
    pass


if __name__ == "__main__":
    main()
