import matplotlib.pyplot as plot
from matplotlib.pyplot import close, savefig
import json
import os
import datetime
import re


def get_date_and_time_now():
    date = datetime.datetime.now().date()
    time = datetime.datetime.now().time()

    return date, time


def arm_corrector(user_input_arm):
    if user_input_arm == "Right":
        return "r"
    if user_input_arm == "Left":
        return "l"
    if user_input_arm != "Left" and user_input_arm != "Right":
        return "incorrect arm input"


def take_value_from_user_json_version(value, date_time):
    """
    take arm and pressure from user
    find date and time now
    return arm, date, time, systolic, diastolic
    """
    str_date = date_time[0].strftime("%d.%m.%Y")
    str_time = date_time[1].strftime("%H:%M")

    systolic_pressure, diastolic_pressure = value

    return str_date, str_time, systolic_pressure, diastolic_pressure


def prepare_data_to_json_writer(user_data, arm):
    """
    Take  arm, str_date, str_time, systolic_pressure, diastolic_pressure
    and add to json file.
    result like: {"r": {"01.01.2000": {"10.00": [140,70]}},
    "l": {"02.02.2002": {"11.00": [140, 60]}}
    """
    arm = arm.lower()
    pressure_dict = read_json_pressure_file()
    str_date, str_time, systolic_pressure, diastolic_pressure = user_data

    if pressure_dict[arm] is not None:
        if str_date in pressure_dict[arm]:
            pressure_dict[arm][str_date][str_time] = [systolic_pressure, diastolic_pressure]
        else:
            pressure_dict[arm][str_date] = {str_time: [systolic_pressure, diastolic_pressure]}

    elif pressure_dict[arm] is None:
        pressure_dict[arm] = {str_date: {str_time: [systolic_pressure, diastolic_pressure]}}

    return pressure_dict


def read_json_pressure_file():
    """
    find pressure.json in OS
    if doesn't exists, create with data {"Right": None, "Left": None}
    """
    try:
        directory = os.path.dirname(os.path.abspath(__file__))
        json_file = os.path.join(directory, 'pressure.json')

        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as read_file:
                return json.load(read_file)
    except json.decoder.JSONDecodeError:
        pass

    return {"r": None, "l": None}


def write_data_to_json_file(pressure_dict):
    """
    find pressure.json in OS
    write new data to the file
    """
    directory = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(directory, 'pressure.json')

    with open(json_file, 'w', encoding="utf-8") as write_file:
        json.dump(pressure_dict, write_file)


def read_and_prepare_json_pressure_file_for_period(arm, first_date, last_date):
    """
    find interval between 2 dates,
    read json file, make two lists for such dates:
    [systolic],[diastolic],[date_list] to graph.
    """
    pressure_dict = read_json_pressure_file()
    arm_dict = pressure_dict[arm]
    systolic, diastolic, date_list = [], [], []

    start = datetime.datetime.strptime(first_date, "%d.%m.%Y")
    end = datetime.datetime.strptime(last_date, "%d.%m.%Y")
    end_date = end + datetime.timedelta(days=1)

    date_generated = [
        (start + datetime.timedelta(days=x)).strftime("%d.%m.%Y")
        for x in range(0, (end_date-start).days)
        ]

    if arm_dict is not None:

        for date in date_generated:

            if len(date_generated) == 1:

                if date not in arm_dict:
                    return "Can't find pressure data"
                else:
                    return read_and_prepare_json_pressure_file_per_day(arm, date)

            elif date in arm_dict:
                date_list.append(date)

                if len(arm_dict[date]) > 1:
                    biggest_pressure = find_biggest_pressure_value_per_day(
                        arm_dict[date]
                        )
                    systolic.append(biggest_pressure[0])
                    diastolic.append(biggest_pressure[1])

                else:
                    for time, value in arm_dict[date].items():
                        systolic.append(value[0])
                        diastolic.append(value[1])
            else:
                continue

        if len(date_list) == 1:
            return read_and_prepare_json_pressure_file_per_day(arm, date_list[0])

        return systolic, diastolic, date_list, arm

    elif arm_dict is None:
        return "Please add arm data"


def read_and_prepare_json_pressure_file_per_day(arm, day):
    """
    take data from json file and return data to day's graph
    like [systolic][diastolic][time_list]
    """
    pressure_dict = read_json_pressure_file()
    arm_dict = pressure_dict[arm]
    systolic, diastolic, time_list = [], [], []

    if arm_dict is not None:
        if day in arm_dict:
            for time in arm_dict[day]:
                time_list.append(time)
                systolic.append(arm_dict[day][time][0])
                diastolic.append(arm_dict[day][time][1])
        else:
            return "Can't find pressure values per day"

        return systolic, diastolic, time_list, arm
    else:
        return "Please add arm data"


def find_biggest_pressure_value_per_day(day_dict):
    """
    take day values,
    find the biggest systolic value
    return [biggest_systolic, diastolic, date, time]
    """
    biggest_value = [0, 0]
    for time in day_dict:
        systolic = int(day_dict[time][0])
        diastolic = int(day_dict[time][1])

        if systolic > int(biggest_value[0]):
            biggest_value = [systolic, diastolic]

        elif systolic == biggest_value[0]:
            if diastolic > biggest_value[1]:
                biggest_value = [systolic, diastolic]

            if diastolic < biggest_value[1]:
                biggest_value = biggest_value
        else:
            continue
    systolic, diastolic = str(biggest_value[0]), str(biggest_value[1])

    return systolic, diastolic


def create_graph(arm_list):
    """
    take [systolic_pressure], [diastolic_pressure], [dates or time]
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


def main():
    arm = input("If you use left arm, print 'l', if right - 'r': ")

    if arm.lower() != "r" and arm.lower() != "l":
        return "Please enter correct arm"

    value = input("Enter your current amounth of arterial_pressure: ")
    list_pressure = re.split(r'[\^\,\.:;\\/]', value)

    if len(list_pressure) == 2 and isinstance(list_pressure, list):
        date_and_time = get_date_and_time_now()
        user_data = take_value_from_user_json_version(list_pressure, date_and_time)

        pressure_dict = prepare_data_to_json_writer(user_data, arm)
        write_data_to_json_file(pressure_dict)

        arm = input("If you need Left-arm graph, press 'l', else: press 'r': ")
        graph_period = input(
            "If you'd like one-day graph, enter date, else, enter 'no': "
            )

        if graph_period.lower() == "no":
            all_the_time = read_and_prepare_json_pressure_file(arm)
            create_graph(all_the_time)
        else:
            per_day = read_and_prepare_json_pressure_file_per_day(arm, graph_period)
            create_graph(per_day)

    else:
        return "Enter correct pressure data"


if __name__ == "__main__":
    main()
