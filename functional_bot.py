import datetime
import psycopg2
import matplotlib.pyplot as plot
import os
from matplotlib.pyplot import close, savefig
from db_settings import config

def select_data_from_postgresql(first_date, last_date, user):
    """
    find dates for the period
    select data for the user and dates
    """
    pressure_list = []

    date_generated = find_dates_in_period(first_date, last_date)

    connection = config()
    cursor = connection.cursor()

    for date in date_generated:
        pressure_data = []
        date_format = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        postgreSQL_select_query = """
            SELECT * FROM pressure WHERE username = %s and date = %s ;
            """
        username = [user, date_format]
        cursor.execute(postgreSQL_select_query, username)

        for row in cursor:
            print(row)

    cursor.close()
    connection.close()

def make_list_for_arm(pressure_list, arm):
    """
    from pressure_list makes list for "l" or "r" arm,
    then prepare them like list with lists (one per date)
    """
    arm_list = []
    for line in pressure_list:
        if line[-1] == arm:
            arm_list.append(line)
        else:
            continue


    pressure_list_new = []
    my_date = datetime.date(2019, 1, 1)
    new_list = []

    for line in arm_list:
        if line[-2] != my_date:
            pressure_list_new.append(new_list)
            my_date = line[-2]
            new_list = []
            new_list.append(line)
        new_list.append(line)

    pressure_list_new.append(new_list)

    del pressure_list_new[0] # TODO make without first empty list

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

    if len(pressure_list_new) == 1: # TODO change style from list[] to naming
        for line in pressure_list_new[0]:
            systolic, diastolic = line[2], line[3]
            time = datetime.datetime.strftime(line[4], "%H:%M")
            date_list.append(time)
            systolic_list.append(systolic)
            diastolic_list.append(diastolic)

        return systolic_list, diastolic_list, date_list, arm

    elif len(pressure_list_new) == 0:
        raise ValueError("There aren't any data per date")


    for day in pressure_list_new:
        date = datetime.datetime.strftime(day[0][5], "%Y-%m-%d") # TODO fix IndexError: list index out of range

        if len(day) == 1:
            systolic, diastolic = day[0][2], day[0][3]
            date_list.append(date)
            systolic_list.append(systolic)
            diastolic_list.append(diastolic)

        if len(day) > 1:
            biggest_value = [0, 0]
            for line in day:
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
            date_list.append(date)
            systolic_list.append(systolic)
            diastolic_list.append(diastolic)

    return systolic_list, diastolic_list, date_list, arm



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
        print('there is an user un the DB')
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
            ) # TODO change timestamp and data in the table

        cursor.execute(postgres_insert_pressure, records_to_pressure)
        cursor.close()
        connection.commit()
        connection.close()


def find_dates_in_period(first_date, last_date):
    """
    find all dates between first date and last date(included the last)
    """
    start_date = datetime.datetime.strptime(first_date, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(last_date, "%d.%m.%Y")
    end = end_date + datetime.timedelta(days=1)

    date_generated = [
        (start_date + datetime.timedelta(days=x)).strftime("%Y-%m-%d")
        for x in range(0, (end-start_date).days)
        ]

    return date_generated


def select_data_from_postgresql(first_date, last_date, user):
    """
    select data for the user and time period
    """
    pressure_list = []
    date_generated = find_dates_in_period(first_date, last_date)
    connection = config()
    cursor = connection.cursor()
    postgreSQL_select_query = """SELECT * FROM pressure WHERE username = %s;"""
    username = user
    cursor.execute(postgreSQL_select_query, [username])

    pressure_data = cursor.fetchall()
    cursor.close()
    connection.close()

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
        return "incorrect arm input"


def create_graph(arm_list):
    """
    take [systolic_pressure], [diastolic_pressure], [dates or time], arm
    and makes graph, save it like r_graph.png or l_graph.png
    """
    plot.close("all")
    figsize = (8, 4)
    fig = plot.figure(figsize=figsize, facecolor='pink', frameon=True)

    ax = fig.add_subplot(111)  # создаем систему координат

    if arm_list[3] == "r":
        plot.title('Right arm')  # название графика
    elif arm_list[3] == "l":
        plot.title('Left arm')
    else:
        return "incorrect arm name"

    list_systolic_pressure = list(map(int, arm_list[0]))  # данные из стр к int
    list_diastolic_pressure = list(map(int, arm_list[1]))

    list_dates = arm_list[2]  # даты из файла для оси x (даты)
    ax.set_xticklabels(list_dates, rotation=10)
    ax.plot(list_dates, list_systolic_pressure)  # строим график
    ax.plot(list_dates, list_diastolic_pressure)

    for ax in fig.axes:  # сетка на графике
        ax.grid(True)

    directory = os.path.dirname(os.path.abspath(__file__))
    if arm_list[3] == "r":
        graph_name = os.path.join(directory, 'r_graph.png')
        savefig(graph_name)
        return 'r_graph.png'

    if arm_list[3] == "l":
        graph_name = os.path.join(directory, 'l_graph.png')
        savefig(graph_name)
        return 'l_graph.png'

    return "Successfully completed"
