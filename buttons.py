from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove


start_buttons = [
    ["ADD PRESSURE", "SHOW GRAPHS"],
    ["SET TIMER", "REMOVE TIMER", "SHOW TIMERS"],
    ["Add or change personal data to better analytics"]
    ]
start_markup = ReplyKeyboardMarkup(start_buttons, one_time_keyboard=True)

sex_buttons = [["male", "female", "other"]]
sex_markup = ReplyKeyboardMarkup(sex_buttons, one_time_keyboard=True)

arm_buttons = [["Right", "Left"]]
arms_markup = ReplyKeyboardMarkup(arm_buttons, one_time_keyboard=True)

work_buttons = [["Active", "Sitting", "Combine"]]
work_markup = ReplyKeyboardMarkup(work_buttons, one_time_keyboard=True)

markup_remove = ReplyKeyboardRemove(selective=False)
