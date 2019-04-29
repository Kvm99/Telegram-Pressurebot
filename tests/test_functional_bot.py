import copy
import datetime
import os
import os.path as path
import psycopg2
import pytest
import struct

import functional_bot
from .data_for_functional_bot_test import (
    pressure_list,
    pressure_list_new,
    empty_pressure_list,
    short_pressure_list,
    systolic_list,
    diastolic_list,
    date_list,
    day_data,
    day_data_v2,
    day_data_v3,
    day_data_v4,
    arm_list,
    arm_list_v2
    )

from functional_bot import (
    make_list_for_arm,
    prepare_data_from_potgresql_to_graph,
    find_dates_in_period,
    select_data_from_postgresql,
    arm_corrector,
    create_graph,
    append_to_lists,
    find_biggest_value_per_day,
    marking_on_coordinate_axes,
    select_data_picked_by_dates
    )

from db_settings import config


def test_make_list_for_arm():
    assert make_list_for_arm(pressure_list, "r") == [
        [
            (109, 'Mary2z', '130', '70',
                datetime.datetime(
                2019, 4, 20, 13, 16, 41, 521658, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
                datetime.date(2019, 4, 20), 'r')
        ],
        [
            (191, 'Mary2z', '123', '67',
                datetime.datetime(
                2019, 4, 22, 15, 44, 39, 444169, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
                datetime.date(2019, 4, 22), 'r'),
            (194, 'Mary2z', '213', '42',
                datetime.datetime(
                2019, 4, 22, 15, 49, 17, 999382, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
                datetime.date(2019, 4, 22), 'r')
        ]
    ]

    with pytest.raises(TypeError) as error:
        assert make_list_for_arm(123, "r") in str(error.value)

    assert make_list_for_arm({}, "r") == []
    assert make_list_for_arm("smth", "r") == []


def test_prepare_data_from_potgresql_to_graph(monkeypatch):

    def make_list_for_arm(pressure_list, arm):
        pressure_list_new_edited = copy.deepcopy(pressure_list_new)
        return pressure_list_new_edited

    def make_list_for_arm_v2(pressure_list, arm):
        pressure_list_new_edited_v2 = copy.deepcopy(empty_pressure_list)
        return pressure_list_new_edited_v2

    def make_list_for_arm_v3(pressure_list, arm):
        pressure_list_new_edited_v3 = copy.deepcopy(short_pressure_list)
        return pressure_list_new_edited_v3

    monkeypatch.setattr(functional_bot, 'make_list_for_arm', make_list_for_arm)
    assert prepare_data_from_potgresql_to_graph(pressure_list, "r") == (
            ["130", "213"], ["70", "42"], ["2019-04-20", "2019-04-22"], "r"
        )

    monkeypatch.setattr(functional_bot, 'make_list_for_arm', make_list_for_arm_v2)
    with pytest.raises(ValueError) as error:
        assert prepare_data_from_potgresql_to_graph(pressure_list, "r") in str(error.value)

    monkeypatch.setattr(functional_bot, 'make_list_for_arm', make_list_for_arm_v3)
    assert prepare_data_from_potgresql_to_graph(pressure_list, "l") == (
            ["130"], ["70"], ["13:16"], "l"
        )


def test_find_biggest_value_per_day():
    assert find_biggest_value_per_day(day_data) == ('213', '42')
    assert find_biggest_value_per_day(day_data_v2) == ('123', '68')

    with pytest.raises(ValueError) as error:
        assert find_biggest_value_per_day(day_data_v3) in str(error.value)

    with pytest.raises(ValueError) as error:
        assert find_biggest_value_per_day(day_data_v4) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_biggest_value_per_day() in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_biggest_value_per_day(None) in str(error.value)


def test_append_to_lists():
    assert append_to_lists(
            [], [], [], "130", "90", "2019-04-21"
        ) == (["130"], ["90"], ["2019-04-21"])

    assert append_to_lists(
        systolic_list, diastolic_list, date_list,
        "150", "90", "2019-04-21"
        ) == (
            ["130", "213", "150"],
            ["70", "42", "90"],
            ["2019-04-20", "2019-04-22", "2019-04-21"]
        )

    assert append_to_lists(
            [], [], [], 100, "90", "2019-04-21"
        ) == ([100], ["90"], ["2019-04-21"])

    assert append_to_lists(
            [], [], [], ["a", "b", "c"], "90", "2019-04-21"
        ) == ([["a", "b", "c"]], ["90"], ["2019-04-21"])

    assert append_to_lists(
            [], [], [], ["a", "b", "c"], {"a": 1, "b": 2}, "2019-04-21"
        ) == ([["a", "b", "c"]], [{"a": 1, "b": 2}], ["2019-04-21"])

    assert append_to_lists(
            [], [], [], "smth", "90", "2019-04-21"
        ) == (["smth"], ["90"], ["2019-04-21"])

    with pytest.raises(AttributeError) as error:
        assert append_to_lists(
            {}, [], [], "130", "90", "2019-04-21"
        ) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert append_to_lists(
            [], [], [], "130", "90",
        ) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert append_to_lists() in str(error.value)


def test_save_pressure_to_postgresql():
    connection = config()
    if connection:
        assert True
        connection.close()


def test_find_dates_in_period():
    assert find_dates_in_period("21.04.2019", "22.04.2019") == [
        "2019-04-21", "2019-04-22"
    ]
    assert find_dates_in_period("21.04.2019", "21.04.2019") == ["2019-04-21"]
    assert find_dates_in_period("01.01.1001", "01.01.1001") == ["1001-01-01"]

    with pytest.raises(NameError) as error:
        assert find_dates_in_period("22.04.2019", "21.04.2019") in str(error.value)

    with pytest.raises(ValueError) as error:
        assert find_dates_in_period('b', 2) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_dates_in_period([], {}, 'x') in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_dates_in_period("01.01.1001") in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_dates_in_period(None) in str(error.value)


def test_select_data_from_postgresql():
    connection = config()
    if connection:
        assert True
        connection.close()

    assert select_data_from_postgresql('smb') == []


def test_select_data_picked_by_dates():
    assert select_data_picked_by_dates(pressure_list, ["2019-04-20"]) == [
        (108, 'Mary2z', '130', '80',
            datetime.datetime(
            2019, 4, 20, 12, 26, 45, 826178, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
            datetime.date(2019, 4, 20), 'l'),

        (109, 'Mary2z', '130', '70',
            datetime.datetime(
            2019, 4, 20, 13, 16, 41, 521658, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
            datetime.date(2019, 4, 20), 'r')
        ]

    assert select_data_picked_by_dates(pressure_list, ["2019-04-20", "2019-04-21"]) == [
        (108, 'Mary2z', '130', '80',
        datetime.datetime(
        2019, 4, 20, 12, 26, 45, 826178, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
        datetime.date(2019, 4, 20), 'l'),

        (109, 'Mary2z', '130', '70',
            datetime.datetime(
            2019, 4, 20, 13, 16, 41, 521658, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
            datetime.date(2019, 4, 20), 'r'),

        (117, 'Mary2z', '100', '50',
            datetime.datetime(
            2019, 4, 21, 22, 1, 30, 840303, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
            datetime.date(2019, 4, 21), 'l'),

        (118, 'Mary2z', '120', '67',
            datetime.datetime(
            2019, 4, 21, 22, 2, 28, 311614, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
            datetime.date(2019, 4, 21), 'l')
    ]

    with pytest.raises(TypeError) as error:
        assert select_data_picked_by_dates(pressure_list, []) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert select_data_picked_by_dates(pressure_list, {}) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert select_data_picked_by_dates("smth", {}) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert select_data_picked_by_dates([1, 2, 2], {}) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert select_data_picked_by_dates(
                pressure_list,
                [datetime.datetime(2019, 4, 20, 12, 26, 45, 826178)]
            ) in str(error.value)

    with pytest.raises(ValueError) as error:
        assert select_data_picked_by_dates(
            pressure_list, ["00.00.00"]) in str(error.value)


def test_arm_corrector():
    assert arm_corrector('Right') == 'r'
    assert arm_corrector('Left') == 'l'
    with pytest.raises(NameError) as error:
        assert arm_corrector('smth') in str(error.value)

    with pytest.raises(NameError) as error:
        assert arm_corrector(1234) in str(error.value)

    with pytest.raises(NameError) as error:
        assert arm_corrector([1, 2, 3, 'c']) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert arm_corrector() in str(error.value)

    with pytest.raises(TypeError) as error:
        assert arm_corrector('Right', "Left") in str(error.value)


def test_create_graph():
    create_graph(arm_list)

    script_path = path.abspath(path.join(os.getcwd(), "../"))
    graph_path = "Right arm_graph.png"
    test_graph_path = "test_graph.png"

    abs_graph_path = os.path.join(script_path, graph_path)
    abs_test_graph_path = os.path.join(script_path, test_graph_path)

    with open(abs_graph_path, 'rb') as f1, \
        open(abs_test_graph_path, 'rb') as f2:

        while True:
            b1, b2 = f1.read(1), f2.read(1)
            if not b1 or not b2:
                break
            i = struct.unpack('B', b1)[0] - struct.unpack('B', b2)[0]

            assert i == 0

    with pytest.raises(IndexError) as error:
        assert create_graph([]) in str(error.value)

    with pytest.raises(KeyError) as error:
        assert create_graph({}) in str(error.value)

    with pytest.raises(ValueError) as error:
        assert create_graph(arm_list_v2) in str(error.value)


def test_marking_on_coordinate_axes():
    assert marking_on_coordinate_axes(arm_list) == (
            "Right arm",
            [130, 150, 140, 160, 150],
            [90, 90, 70, 90, 90]
        )

    with pytest.raises(ValueError) as error:
        assert marking_on_coordinate_axes(arm_list_v2) in str(error.value)

    with pytest.raises(IndexError) as error:
        assert marking_on_coordinate_axes([]) in str(error.value)

    with pytest.raises(KeyError) as error:
        assert marking_on_coordinate_axes({}) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert marking_on_coordinate_axes('a', 'b', 'c') in str(error.value)
