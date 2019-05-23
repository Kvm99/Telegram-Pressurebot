import datetime


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

    return pressure_list_new


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
    """
    Take pressure data per day and find
    biggest value.
    If some systolic and other systolic equal,
    compare by diastolic
    """
    values = [(data[2], data[3]) for data in day_data]
    systolic, diastolic = max(values)

    return systolic, diastolic
