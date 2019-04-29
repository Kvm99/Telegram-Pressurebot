import copy
import datetime
import json
import os
import pytest
import struct
import sys  
import prepare_and_show_graph

from .data_for_tests import (
    test_pressure_dict,
    pressure_dict_empty_l_arm,
    pressure_dict_empty_r_arm,
    test_pressure_dict_for_one_day,
    day_dict,
    arm_list,
    many_days_pressure_dict,
    )

from prepare_and_show_graph import (
    get_date_and_time_now,
    arm_corrector,
    take_value_from_user_json_version,
    create_graph,
    read_json_pressure_file,
    write_data_to_json_file,
    prepare_data_to_json_writer,
    read_and_prepare_json_pressure_file,
    read_and_prepare_json_pressure_file_for_period,
    read_and_prepare_json_pressure_file_per_day,
    find_biggest_pressure_value_per_day,
    create_graph,
    )


FAKE_DATETIME = datetime.datetime(2020, 12, 25, 12, 41, 23, 108918)
FAKE_DATE = FAKE_DATETIME.date()
FAKE_TIME = FAKE_DATETIME.time()
PATH = '/home/mary/Documents/study/HomePatProjHealth/test_pressure.json'


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_DATETIME

    monkeypatch.setattr(datetime, 'datetime', mydatetime)

def test_get_date_and_time_now(patch_datetime_now):
    assert datetime.datetime.now() == FAKE_DATETIME
    assert len(get_date_and_time_now()) == 2
    date, time = get_date_and_time_now()
    assert date == FAKE_DATE
    assert time == FAKE_TIME


def test_arm_corrector():
    assert arm_corrector("Right") == "r"
    assert arm_corrector("Left") == "l"
    assert arm_corrector("Smth") == "incorrect arm input"
    assert arm_corrector(123) == "incorrect arm input"
    assert arm_corrector([12365, 'smth']) == "incorrect arm input"

    with pytest.raises(TypeError) as error:
        assert arm_corrector("Smth", "anyth") in str(error.value)


def test_take_value_from_user_json_version():
    str_date, str_time, systolic_pressure, diastolic_pressure = take_value_from_user_json_version(['140','30'], [FAKE_DATE, FAKE_TIME])

    assert len(take_value_from_user_json_version(['140','30'], [FAKE_DATE, FAKE_TIME])) == 4
    assert str_date == "25.12.2020"
    assert str_time == "12:41"
    assert take_value_from_user_json_version(['140','30'], [FAKE_DATE, FAKE_TIME]) == ("25.12.2020", "12:41", "140", "30")

    with pytest.raises(TypeError) as error:
        assert take_value_from_user_json_version(2, ['140','30'], [FAKE_DATE, FAKE_TIME]) in str(error.value)
   

@pytest.fixture
def patch_os_path_join(monkeypatch):
    def join(*args, **kwargs):
        return PATH

    monkeypatch.setattr(os.path, 'join', join)


def test_read_json_pressure_file(patch_os_path_join):
    with open(PATH, "w", encoding="utf-8") as read_file:
        json.dump("just a text", read_file)
        assert read_json_pressure_file() == {"r": None, "l": None}
    
    with open(PATH, "w", encoding="utf-8") as read_file:
        json.dump(test_pressure_dict, read_file)
        
    with open(PATH, "r", encoding="utf-8") as file_to_read:
        assert read_json_pressure_file() == json.load(file_to_read)
    

def test_write_data_to_json_file(patch_os_path_join):
    with open(PATH, "w", encoding="utf-8") as read_file:
        json.dump(test_pressure_dict, read_file)
    with open(PATH, "r", encoding="utf-8") as file_to_read:
        assert read_json_pressure_file() == json.load(file_to_read)


def test_prepare_data_to_json_writer(monkeypatch):

    def read_json_pressure_file1():
        pressure_dict = copy.deepcopy(test_pressure_dict)
        return pressure_dict

    def read_json_pressure_file2():
        dict_empty_l_arm = copy.deepcopy(pressure_dict_empty_l_arm)
        return dict_empty_l_arm

    def read_json_pressure_file3():
        dict_empty_r_arm = copy.deepcopy(pressure_dict_empty_r_arm)
        return dict_empty_r_arm

    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file1)

    # add pressure value (right arm) with a new date:
    assert prepare_data_to_json_writer(["03.03.2019", "21:30", "150", "70"], "r") == {
    "r": {
        "03.03.2019": {"21:30" : ["150", "70"]},
        "21.03.2019": {
            "15:28": ["130", "90"], 
            "15:30": ["150", "90"],
            "15:41": ["140", "70"], 
            "15:46": ["160", "90"], 
            "15:49": ["150", "90"]
            },
        "22.03.2019": {
            "12:00": ["120", "50"]
            }
        },
    "l": {
        "21.03.2019": {
            "21:34": ["140", "79"],
            "21:35": ["130", "80"]
            },
        "26.03.2019": {
            "15:22": ["100", "20"],
            "16:12": ["300", "30"]
            }
        }
    }
    
    # add pressure value (left arm) with a new date:
    assert prepare_data_to_json_writer(["04.03.2019", "21:30", "150", "70"], "l") == {
    "r": {
        "21.03.2019": {
            "15:28": ["130", "90"],
            "15:30": ["150", "90"],
            "15:41": ["140", "70"],
            "15:46": ["160", "90"],
            "15:49": ["150", "90"]
            },
        "22.03.2019": {
            "12:00": ["120", "50"]
            }
        },
    "l": {
        "04.03.2019": {"21:30" : ["150", "70"]},
        "21.03.2019": {
            "21:34": ["140", "79"],
            "21:35": ["130", "80"]
            },
        "26.03.2019": {
            "15:22": ["100", "20"],
            "16:12": ["300", "30"]
            }
        }
    }

    # add pressure value (right arm) with an existed date:
    assert prepare_data_to_json_writer(["21.03.2019", "07:30", "150", "70"], "r") == {
    "r": {
        "21.03.2019": {
            "07:30": ["150", "70"],
            "15:28": ["130", "90"],
            "15:30": ["150", "90"],
            "15:41": ["140", "70"],
            "15:46": ["160", "90"],
            "15:49": ["150", "90"]
            },
        "22.03.2019": {
            "12:00": ["120", "50"]
            }
        },
    "l": {
        "21.03.2019": {
            "21:34": ["140", "79"],
            "21:35": ["130", "80"]
            },
        "26.03.2019": {
            "15:22": ["100", "20"],
            "16:12": ["300", "30"]
            }
        }
    }

    # add pressure value (left arm) with an existed date:
    assert prepare_data_to_json_writer(["21.03.2019", "07:30", "150", "70"], "l") == {
    "r": {
        "21.03.2019": {
            "15:28": ["130", "90"],
            "15:30": ["150", "90"],
            "15:41": ["140", "70"],
            "15:46": ["160", "90"],
            "15:49": ["150", "90"]
            },
        "22.03.2019": {
            "12:00": ["120", "50"]
            }
        },
    "l": {
        "21.03.2019": {
            "07:30": ["150", "70"],
            "21:34": ["140", "79"],
            "21:35": ["130", "80"]
            },
        "26.03.2019": {
            "15:22": ["100", "20"],
            "16:12": ["300", "30"]
            }
        }
    }

    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file3)


    # add pressure value (right arm) if "r": None:
    assert prepare_data_to_json_writer(["21.03.2019", "07:30", "150", "70"], "r") == {
    "r": {
        "21.03.2019": {"07:30": ["150", "70"]}},
    "l": {
        "21.03.2019": {
            "21:34": ["140", "79"],
            "21:35": ["130", "80"]
            },
        "26.03.2019": {
            "15:22": ["100", "20"],
            "16:12": ["300", "30"]
            }
        }
    }

    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file2)

    # add pressure value (left arm) if "l": None:
    assert prepare_data_to_json_writer(["21.03.2019", "07:30", "150", "70"], "l") == {
    "r": {
        "21.03.2019": {
            "15:28": ["130", "90"],
            "15:30": ["150", "90"],
            "15:41": ["140", "70"],
            "15:46": ["160", "90"],
            "15:49": ["150", "90"]
            }
        },
    "l": {
        "21.03.2019": {"07:30": ["150", "70"]}
        }
    }

    with pytest.raises(TypeError) as error:
        assert prepare_data_to_json_writer("smth", ["21.03.2019", "07:30", "150", "70"], "l") in str(error.value)


def test_read_and_prepare_json_pressure_file(monkeypatch):

    def read_json_pressure_file1():
        pressure_dict = copy.deepcopy(test_pressure_dict)
        return pressure_dict

    def read_json_pressure_file2():
        pressure_dict = copy.deepcopy(test_pressure_dict_for_one_day)
        return pressure_dict

    def read_json_pressure_file3():
        pressure_dict = copy.deepcopy(pressure_dict_empty_r_arm)
        return pressure_dict

    def read_json_pressure_file4():
        pressure_dict = copy.deepcopy(pressure_dict_empty_l_arm)
        return pressure_dict
    

    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file1)
    # if is's a many day presure data
    assert read_and_prepare_json_pressure_file("r") == (["160", "120"], ["90", "50"], ["21.03.2019", "22.03.2019"], "r")
    assert read_and_prepare_json_pressure_file("l") == (["140", "300"], ["79", "30"], ["21.03.2019", "26.03.2019"], "l")


    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file2)
    # if is's one day presure data
    assert read_and_prepare_json_pressure_file("r") == (
            ["130", "150", "140", "160", "150"],
            ["90", "90", "70", "90", "90"],
            ["15:28", "15:30", "15:41", "15:46", "15:49"],
            "r")

    assert read_and_prepare_json_pressure_file("l") == (
            ["140", "130"],
            ["79", "80"],
            ["21:34", "21:35"],
            "l")
    # if is's None in arm dict
    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file3)
    assert read_and_prepare_json_pressure_file("r") == "Please add arm data"

    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file4)
    assert read_and_prepare_json_pressure_file("l") == "Please add arm data"

    with pytest.raises(KeyError) as error:
        assert read_and_prepare_json_pressure_file("f") in str(error.value)

    with pytest.raises(TypeError) as error:
        assert read_and_prepare_json_pressure_file("f", "l") in str(error.value)


def test_read_and_prepare_json_pressure_file_for_period(monkeypatch):
    def read_json_pressure_file():
        pressure_dict = copy.deepcopy(many_days_pressure_dict)
        return pressure_dict

    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file)

    assert read_and_prepare_json_pressure_file_for_period('r', "22.03.2019", "24.03.2019") == (
            ["120", "100", "120"],
            ["50", "50", "50"],
            ["22.03.2019", "23.03.2019", "24.03.2019"],
            "r")

    #if more then one pressure data per day
    assert read_and_prepare_json_pressure_file_for_period('r', "21.03.2019", "24.03.2019") == (
            ["160", "120", "100", "120"],
            ["90", "50", "50", "50"],
            ["21.03.2019", "22.03.2019", "23.03.2019", "24.03.2019"],
            "r")

    with pytest.raises(KeyError) as error: 
        assert read_and_prepare_json_pressure_file_for_period('p', "22.03.2019", "24.03.2019") in str(error.value)

    #if data doesn't existed in user perssure file
    with pytest.raises(KeyError) as error: 
        assert read_and_prepare_json_pressure_file_for_period('r', "20.03.2019", "24.03.2019") in str(error.value)

    with pytest.raises(TypeError) as error: 
        assert read_and_prepare_json_pressure_file_for_period('r', "20.03.2019", "24.03.2019", "smth") in str(error.value)


def test_read_and_prepare_json_pressure_file_per_day(monkeypatch):

    def read_json_pressure_file1():
        pressure_dict = copy.deepcopy(test_pressure_dict)
        return pressure_dict

    def read_json_pressure_file2():
        pressure_dict = copy.deepcopy(pressure_dict_empty_r_arm)
        return pressure_dict

    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file1)

    assert read_and_prepare_json_pressure_file_per_day("r", "21.03.2019") == (
            ["130", "150", "140", "160", "150"],
            ["90", "90", "70", "90", "90"],
            ["15:28", "15:30", "15:41", "15:46", "15:49"],
            "r")

    assert read_and_prepare_json_pressure_file_per_day("l", "26.03.2019") == (
            ["100", "300"],
            ["20", "30"],
            ["15:22", "16:12"],
            "l")

    assert read_and_prepare_json_pressure_file_per_day("l", "00.00.0000") == "Can't find pressure values per day"

    monkeypatch.setattr(prepare_and_show_graph, 'read_json_pressure_file', read_json_pressure_file2)

    assert read_and_prepare_json_pressure_file_per_day("r", "20.03.2019") == "Please add arm data"

    with pytest.raises(KeyError) as error:
        assert read_and_prepare_json_pressure_file_per_day("f", "20.03.2019") in str(error.value)


def test_find_biggest_pressure_value_per_day():
    assert find_biggest_pressure_value_per_day(day_dict) == ("160", "90")

    with pytest.raises(ValueError) as error:
        assert find_biggest_pressure_value_per_day({'a': 'b', 'two': 'three'}) in str(error.value)

    with pytest.raises(TypeError) as error:
        assert find_biggest_pressure_value_per_day([1, 2, 3, 'c']) in str(error.value)


def test_create_graph():
    
    with pytest.raises(ValueError) as error:
        assert create_graph([["2"], ["l"], ["202"], "l"]) in str(error.value)

    with pytest.raises(IndexError) as error:
        assert create_graph([["2"], ["l"], ["202"]]) in str(error.value)

    with pytest.raises(TypeError) as error: 
        assert create_graph(1255) in str(error.value)

    assert create_graph(["1", {"1": "smth"}, "r", "smth"]) == "incorrect arm name"
   
    create_graph(arm_list)

    with open('r_graph.png','rb') as f1, \
        open('test_graph.png','rb') as f2:
        
        while True:
            b1, b2 = f1.read(1), f2.read(1)
            if not b1 or not b2:
                break
            i = struct.unpack('B', b1)[0] - struct.unpack('B', b2)[0]

            assert i == 0
