import datetime
import psycopg2
import matplotlib.pyplot as plot
import os
from matplotlib.pyplot import savefig
from db_settings import config


def make_list_for_arm(pressure_list, arm):
    """
    from pressure_list makes list for "l" or "r" arm,
    then prepare them like list with lists (one per date)
    """
    arm_list = [line for line in pressure_list if line[-1]==arm]

    pressure_list_new = []
    comparison_date = datetime.date(1, 1, 1)
    new_list = []

    for line in arm_list:
        date = line[-2]

        if date > comparison_date:
            new_list = []
            new_list.append(line)
            pressure_list_new.append(new_list)
            comparison_date = date
        else:
            new_list.append(line)

    return pressure_list_new


def prepare_data_from_potgresql_to_graph(pressure_list, arm):
    """
    if it's only one-day data, make graph with time-indexes,
    if there are a lot of days and pressure-records,
    find the biggest value per each day.
    return: [systolic],[diastolic],[date_list], arm
    """
    pressure_list_new = make_list_for_arm(pressure_list, arm)

    systolic_list, diastolic_list, date_list = [], [], []

    if len(pressure_list_new) == 0:
        raise ValueError("There aren't any data per date")

    elif len(pressure_list_new) == 1:
        for each_time in pressure_list_new[0]:
            systolic, diastolic = each_time[2], each_time[3]
            time = datetime.datetime.strftime(each_time[4], "%H:%M")

            systolic_list, diastolic_list, date_list =  append_to_lists(
                systolic_list, diastolic_list, date_list, systolic, diastolic, time
                )

        return systolic_list, diastolic_list, date_list, arm

    for day in pressure_list_new:
        date = datetime.datetime.strftime(day[0][5], "%Y-%m-%d")

        if len(day) == 1:
            systolic, diastolic = day[0][2], day[0][3]
            systolic_list, diastolic_list, date_list = append_to_lists(
                systolic_list, diastolic_list, date_list, systolic, diastolic, date
                )

        if len(day) > 1:
            systolic, diastolic = find_biggest_value_per_day(day)
            systolic_list, diastolic_list, date_list = append_to_lists(
                systolic_list, diastolic_list, date_list, systolic, diastolic, date
                )

    return systolic_list, diastolic_list, date_list, arm


def append_to_lists(
    systolic_list, diastolic_list, date_list, systolic, diastolic, date
    ):
    """
    Append systolic, diastolic, date to similar lists
    """
    systolic_list.append(systolic)
    diastolic_list.append(diastolic)
    date_list.append(date)

    return systolic_list, diastolic_list, date_list


def find_biggest_value_per_day(day_data):
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
        username, systolic, diastolic, timestamp, date, arm
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
            username, systolic, diastolic, timestamp, date, arm
            )
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        records_to_pressure = (
            username,
            systolic,
            diastolic,
            timestamp,
            date,
            arm
            )  # TODO change timestamp and data in the table

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
        postgres_insert_users = """INSERT INTO users (
        username, sex, age, weight, work
        ) VALUES (%s, %s, %s, %s, %s)"""
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
        cursor.execute(
            """
            UPDATE users SET 
            sex={}, age={}, weight={}, work={} WHERE username LIKE {}
            """.format(sex, age, weight, work, user_name)
            )

        #VALUES (%s, %s, %s, %s, %s)"""
        #values = (sex, age, weight, work, username)
        #cursor.execute(add_sex, values)

    finally:   
        cursor.close()
        connection.commit()
        connection.close()


def find_dates_in_period(first_date, last_date):
    """
    find all dates between first date and last date(included the last)
    """
    start_date = datetime.datetime.strptime(first_date, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(last_date, "%d.%m.%Y")

    if start_date == end_date:
        return [start_date.strftime("%Y-%m-%d")] 

    elif end_date > start_date:
        end = end_date + datetime.timedelta(days=1)

        date_generated = [
            (start_date + datetime.timedelta(days=x)).strftime("%Y-%m-%d")
            for x in range(0, (end-start_date).days)
            ]

        return date_generated

    else:
        raise NameError('Sequence of days is broken')


def select_data_from_postgresql(user):
    """
    select data for the user and time period
    """
    connection = config()
    cursor = connection.cursor()
    postgreSQL_select_query = """SELECT * FROM pressure WHERE username = %s;"""
    username = user
    cursor.execute(postgreSQL_select_query, [username])

    pressure_data = cursor.fetchall()
    cursor.close()
    connection.close()

    return pressure_data


def select_data_picked_by_dates(pressure_data, date_generated):
    """
    take all selected date from DB
    and find only for requested dates
    """
    pressure_list = []
    for line in pressure_data:

        for date in date_generated:
            date_format = datetime.datetime.strptime(date, "%Y-%m-%d").date()

            if date_format == line[5]:
                pressure_list.append(line)

    return pressure_list


def arm_corrector(user_input_arm):
    """
    receive user input data (right or left arm)
    and convert them into needed type ('r' or 'l')
    """
    if user_input_arm == "Right":
        return "r"
    if user_input_arm == "Left":
        return "l"
    if user_input_arm != "Left" and user_input_arm != "Right":
        raise NameError('incorrect arm input')


def create_graph(arm_list):
    """
    take [systolic_pressure], [diastolic_pressure], [dates or time], arm

    and makes graph, save it like r_graph.png or l_graph.png
    """
    plot.close("all")
    figsize = (8, 4)
    fig = plot.figure(figsize=figsize, facecolor='pink', frameon=True)

    ax = fig.add_subplot(111)

    arm, list_systolic_pressure, list_diastolic_pressure = \
        marking_on_coordinate_axes(arm_list)

    plot.title(arm)
    dates = arm_list[2]
    ax.set_xticklabels(dates, rotation=10)
    ax.plot(dates, list_systolic_pressure)
    ax.plot(dates, list_diastolic_pressure)

    for ax in fig.axes:
        ax.grid(True)

    directory = os.path.dirname(os.path.abspath(__file__))
    graph_name = os.path.join(directory, '%s_graph.png' %arm)
    savefig(graph_name)

    return '%s_graph.png' %arm


def marking_on_coordinate_axes(arm_list):
    if arm_list[3] == "r":
        arm = "Right arm"
    elif arm_list[3] == "l":
        arm = "Left arm"
    else:
        raise ValueError("Incorrect arm name")

    list_systolic_pressure = list(map(int, arm_list[0]))
    list_diastolic_pressure = list(map(int, arm_list[1]))

    return arm, list_systolic_pressure, list_diastolic_pressure
