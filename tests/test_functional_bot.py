import datetime
import os
import os.path as path
import psycopg2
import pytest
import struct

from .tests_data.data_for_functional_bot_test import (
    pressure_list,
    pressure_list_v2,
    pressure_list_new,
    pressure_list_new_v2,
    pressure_list_new_v3,
    pressure_list_new_v4,
    pressure_list_new_v5,
    pressure_list_new_v6,
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
from helpers.analytics import (
    analysis_pressure_value,
    analysis_pressure_difference,
    analysis_result
)
from helpers.graph import (
    if_dates_consecutive,
    prepare_data_from_potgresql_to_graph,
    create_graph,
    marking_on_coordinate_axes,
)
from helpers.prepare_data import (
    make_list_for_arm,
    prepare_data_for_one_day,
    prepare_data_for_many_days,
    append_to_lists,
    find_biggest_value_per_day
)


def test_make_list_for_arm_if_days():
    assert make_list_for_arm(pressure_list, "Right") == [
                [
                    (109, 'Mary2z', '130', '70',
                        datetime.datetime(
                            2019, 4, 20, 13, 16, 41, 521658,
                            tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                offset=180,
                                name=None
                            )
                        ),
                        'Right', '80')
                ],
                [
                    (191, 'Mary2z', '123', '67',
                        datetime.datetime(
                            2019, 4, 22, 15, 44, 39, 444169,
                            tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                offset=180, name=None
                                )
                            ),
                        'Right', '80')
                ]
            ]

    assert make_list_for_arm(pressure_list, "Left") == [
                [
                    (108, 'Mary2z', '130', '80',
                        datetime.datetime(
                            2019, 4, 20, 12, 26, 45, 826178,
                            tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                offset=180, name=None
                            )
                        ),
                        'Left', '80')
                ],
                [
                    (117, 'Mary2z', '100', '50',
                        datetime.datetime(
                            2019, 4, 21, 22, 1, 30, 840303,
                            tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                offset=180, name=None
                            )
                        ),
                        'Left', '80'),
                    (118, 'Mary2z', '120', '67',
                        datetime.datetime(
                            2019, 4, 21, 22, 2, 28, 311614,
                            tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                offset=180,
                                name=None
                                )
                            ),
                        'Left', '80'),
                ],
                [
                    (192, 'Mary2z', '123', '67',
                        datetime.datetime(
                            2019, 4, 22, 15, 46, 58, 363557,
                            tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                offset=180, name=None
                                )
                            ),
                        'Left', '80'),

                    (194, 'Mary2z', '213', '42',
                        datetime.datetime(
                            2019, 4, 22, 15, 49, 17, 999382,
                            tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                offset=180, name=None
                            )
                        ),
                        'Left', '80')
                ]
            ]


def test_make_list_for_arm_if_day():
    assert make_list_for_arm(pressure_list_v2, "Left") == [
        [
            (192, 'Mary2z', '123', '67',
                datetime.datetime(
                    2019, 4, 22, 15, 46, 58, 363557,
                    tzinfo=psycopg2.tz.FixedOffsetTimezone(
                        offset=180,
                        name=None
                        )
                    ),
                'Left', '80'),

            (194, 'Mary2z', '213', '42',
                datetime.datetime(
                    2019, 4, 22, 15, 49, 17, 999382,
                    tzinfo=psycopg2.tz.FixedOffsetTimezone(
                        offset=180, name=None
                    )
                ),
                'Left', '80')
        ]
    ]

    assert make_list_for_arm(pressure_list_v2, "Right") == [
        [
            (191, 'Mary2z', '123', '67',
                datetime.datetime(
                    2019, 4, 22, 15, 44, 39, 444169,
                    tzinfo=psycopg2.tz.FixedOffsetTimezone(
                        offset=180, name=None
                    )
                ),
                'Right', '80')
        ]
    ]


def test_make_list_for_arm_if_no_day():
    assert make_list_for_arm({}, "Right") == []

    with pytest.raises(TypeError) as error:
        assert make_list_for_arm(123, "Left") in str(error.value)

    with pytest.raises(IndexError) as error:
        assert make_list_for_arm("smth", "Right") in str(error.value)


def test_prepare_data_from_potgresql_to_graph_if_empty():
    with pytest.raises(ValueError) as error:
        assert prepare_data_from_potgresql_to_graph(
            [],
            "Right"
        ) in str(error.value)

    with pytest.raises(ValueError) as error:
        assert prepare_data_from_potgresql_to_graph(
            [],
            "Left"
        ) in str(error.value)


def test_prepare_data_from_potgresql_to_graph_if_one_day():
    assert prepare_data_from_potgresql_to_graph(pressure_list_v2, "Right") == (
            ['123'], ['67'], ['15:44'], 'Right'
        )

    assert prepare_data_from_potgresql_to_graph(pressure_list_v2, "Left") == (
            ['123', '213'], ['67', '42'], ['15:46', '15:49'], 'Left'
        )


def test_prepare_data_from_potgresql_to_graph_if_many_days():
    assert prepare_data_from_potgresql_to_graph(pressure_list, "Right") == (
            ['130', '123'], ['70', '67'], ['2019-04-20', '2019-04-22'], 'Right'
        )

    assert prepare_data_from_potgresql_to_graph(pressure_list, "Left") == (
            ['130', '120', '213'],
            ['80', '67', '42'],
            ['2019-04-20', '2019-04-21', '2019-04-22'],
            'Left'
        )


def test_prepare_data_from_potgresql_to_graph_if_other():
    with pytest.raises(TypeError) as error:
        assert prepare_data_from_potgresql_to_graph(
            123,
            "Left"
        ) in str(error.value)

    with pytest.raises(ValueError) as error:
        assert prepare_data_from_potgresql_to_graph(
            [],
            "Left"
        ) in str(error.value)

    with pytest.raises(ValueError) as error:
        assert prepare_data_from_potgresql_to_graph(
            {},
            "Left"
        ) in str(error.value)

    with pytest.raises(IndexError) as error:
        assert prepare_data_from_potgresql_to_graph(
            'smth', "Left"
        ) in str(error.value)


def test_prepare_data_for_one_day_if_data():
    assert prepare_data_for_one_day(pressure_list_new_v2, "Right") == (
            ['130', '213'], ['70', '42'], ['13:16', '15:49'], 'Right'
        )

    assert prepare_data_for_one_day(pressure_list_new_v3, "Left") == (
            ['130', '213'], ['70', '42'], ['13:16', '15:49'], 'Left'
        )


def test_prepare_data_for_one_day_if_other():
    with pytest.raises(IndexError) as error:
        assert prepare_data_for_one_day([], "Right") in str(error.value)

    with pytest.raises(KeyError) as error:
        assert prepare_data_for_one_day({}, "Left") in str(error.value)

    with pytest.raises(TypeError) as error:
        assert prepare_data_for_one_day(123, "Right") in str(error.value)

    with pytest.raises(IndexError) as error:
        assert prepare_data_for_one_day('smth', "Left") in str(error.value)


def test_prepare_data_for_many_days_if_many_data_per_day():
    assert prepare_data_for_many_days(pressure_list_new, "Right") == (
            ['130', '213'], ['70', '42'], ['2019-04-20', '2019-04-22'], 'Right'
        )

    assert prepare_data_for_many_days(pressure_list_new_v4, "Left") == (
            ['130', '213'], ['70', '42'], ['2019-04-20', '2019-04-22'], 'Left'
        )


def test_prepare_data_for_many_days_if_one_data_per_day():
    assert prepare_data_for_many_days(pressure_list_new_v5, "Right") == (
            ['120', '213'], ['70', '42'], ['2019-04-20', '2019-04-22'], 'Right'
        )

    assert prepare_data_for_many_days(pressure_list_new_v6, "Left") == (
            ['120', '213'], ['70', '42'], ['2019-04-20', '2019-04-22'], 'Left'
        )


def test_prepare_data_for_many_days_if_no_data():
    assert prepare_data_for_many_days([], "Right") == (
            [], [], [], 'Right'
        )


def test_prepare_data_for_many_days_if_other():
    assert prepare_data_for_many_days({}, "Right") == (
            [], [], [], 'Right'
        )
    with pytest.raises(IndexError) as error:
        assert prepare_data_for_many_days('smth', "Left") in str(error.value)

    with pytest.raises(TypeError) as error:
        assert prepare_data_for_many_days(123, "Right") in str(error.value)


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


def test_find_biggest_value_per_day():
    assert find_biggest_value_per_day(day_data) == ('213', '42')
    assert find_biggest_value_per_day(day_data_v2) == ('123', '68')

    with pytest.raises(TypeError) as error:
        assert find_biggest_value_per_day(day_data_v3) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_biggest_value_per_day(day_data_v4) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_biggest_value_per_day() in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_biggest_value_per_day(None) in str(error.value)


def test_if_dates_consecutive():
    assert if_dates_consecutive('2019-02-04', '2019-02-04') is True
    assert if_dates_consecutive('2019-02-04', '2019-02-05') is True


def test_if_dates_consecutive_other():
    assert if_dates_consecutive('2019-02-04', '2019-02-03') is None

    with pytest.raises(TypeError) as error:
        assert if_dates_consecutive(2019, '2019-02-05') in str(error.value)

    with pytest.raises(ValueError) as error:
        assert if_dates_consecutive('a', '2019-02-05') in str(error.value)

    with pytest.raises(TypeError) as error:
        assert if_dates_consecutive({}, '2019-02-05') in str(error.value)

    with pytest.raises(ValueError) as error:
        assert if_dates_consecutive('', '') in str(error.value)


def test_create_graph():
    create_graph(arm_list)

    script_path = path.abspath(path.join(os.getcwd()))
    graph_path = "tests/tests_data/test_graph.png"
    test_graph_path = "tests/tests_data/test_graph_v2.png"

    abs_graph_path = os.path.join(script_path, graph_path)
    abs_test_graph_path = os.path.join(script_path, test_graph_path)

    with open(abs_graph_path, 'rb') as f1:
        with open(abs_test_graph_path, 'rb') as f2:

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
            "Right",
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


def test_analysis_pressure_value():
    assert analysis_pressure_value('130', '90') == "Good"

    assert analysis_pressure_value('150', '90') == '''
            Not good.
            You'd better lay down and take medecine
            '''

    assert analysis_pressure_value('90', '90') == '''
            Not good.
            What about a cup of strong tea or coffee?
            '''
    with pytest.raises(TypeError) as error:
        assert analysis_pressure_value(90, '90') in str(error.value)

    with pytest.raises(ValueError) as error:
        assert analysis_pressure_value('smth', '90') in str(error.value)

    with pytest.raises(ValueError) as error:
        assert analysis_pressure_value('', '90') in str(error.value)

    with pytest.raises(TypeError) as error:
        assert analysis_pressure_value([], '90') in str(error.value)


def test_analysis_pressure_difference():
    assert analysis_pressure_difference('130', '90') == "Good"

    assert analysis_pressure_difference('130', '60') == '''
            You shold go to cardiologist,
            because your difference between systolic
            and diastolic pressure is dangerous
            '''

    with pytest.raises(TypeError) as error:
        assert analysis_pressure_difference([], '90') in str(error.value)

    with pytest.raises(ValueError) as error:
        assert analysis_pressure_difference('', '90') in str(error.value)


def test_analysis_result():
    assert analysis_result('130', '90') == "Great values!"

    assert analysis_result('130', '50') == '''
            You shold go to cardiologist,
            because your difference between systolic
            and diastolic pressure is dangerous
            '''

    assert analysis_result('150', '111') == '''
            Not good.
            You'd better lay down and take medecine
            '''
