import datetime
import psycopg2

pressure_list = [
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
		datetime.date(2019, 4, 21), 'l'),

	(191, 'Mary2z', '123', '67',
		datetime.datetime(
		2019, 4, 22, 15, 44, 39, 444169, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
		datetime.date(2019, 4, 22), 'r'),

	(192, 'Mary2z', '123', '67',
		datetime.datetime(
		2019, 4, 22, 15, 46, 58, 363557, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
		datetime.date(2019, 4, 22), 'l'),

	(194, 'Mary2z', '213', '42',
		datetime.datetime(
		2019, 4, 22, 15, 49, 17, 999382, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
		datetime.date(2019, 4, 22), 'r')
]


pressure_list_new = [
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

empty_pressure_list = []

short_pressure_list = [
			(109, 'Mary2z', '130', '70',
			datetime.datetime(
			2019, 4, 20, 13, 16, 41, 521658, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)), 
			datetime.date(2019, 4, 20), 'l')
			]

systolic_list, diastolic_list, date_list = ["130", "213"], ["70", "42"], ["2019-04-20", "2019-04-22"]

day_data = [
			(191, 'Mary2z', '123', '67',
			datetime.datetime(
			2019, 4, 22, 15, 44, 39, 444169, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
			datetime.date(2019, 4, 22), 'r'),
			(194, 'Mary2z', '213', '42',
			datetime.datetime(
			2019, 4, 22, 15, 49, 17, 999382, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
			datetime.date(2019, 4, 22), 'r')
		]

day_data_v2 = [
			(191, 'Mary2z', '123', '67',
			datetime.datetime(
			2019, 4, 22, 15, 44, 39, 444169, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
			datetime.date(2019, 4, 22), 'r'),
			(194, 'Mary2z', '123', '68',
			datetime.datetime(
			2019, 4, 22, 15, 49, 17, 999382, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
			datetime.date(2019, 4, 22), 'r')
		]

day_data_v3 = [
			(191, 'Mary2z', 'b', 'a',
			datetime.datetime(
			2019, 4, 22, 15, 44, 39, 444169, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
			datetime.date(2019, 4, 22), 'r'),
			(194, 'Mary2z', '123', '68',
			datetime.datetime(
			2019, 4, 22, 15, 49, 17, 999382, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
			datetime.date(2019, 4, 22), 'r')
		]

day_data_v4 = [
			(191, 'Mary2z', b'Byte', 'a',
			datetime.datetime(
			2019, 4, 22, 15, 44, 39, 444169, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
			datetime.date(2019, 4, 22), 'r'),
			(194, 'Mary2z', '123', '68',
			datetime.datetime(
			2019, 4, 22, 15, 49, 17, 999382, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)),
			datetime.date(2019, 4, 22), 'r')
		]

arm_list = [
	["130", "150", "140", "160", "150" ],
	["90", "90", "70", "90", "90"],
	["15:28", "15:30", "15:41", "15:46", "15:49"],
	'r']

arm_list_v2 = [
	["130", "150", "140", "160", "150" ],
	["90", "90", "70", "90", "90"],
	["15:28", "15:30", "15:41", "15:46", "15:49"],
	'f']