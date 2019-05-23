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

    if difference < 65:
        return "Good"

    elif difference >= 65:
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
