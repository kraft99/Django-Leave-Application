import datetime
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError



class TimeStamp(models.Model):
	"""
	Model : This is an Abstract Model for All Model Classes
	"""
	created = models.DateTimeField(auto_now_add=True,auto_now=False)
	updated = models.DateTimeField(auto_now_add=False,auto_now=True)

	class Meta:
		abstract = True




def is_not_weekday(date_obj):
	"""
	Method: Checks if a given date falls on a weekend ie. Saturday or Sunday
	"""
	return bool(True if not (date_obj.isoweekday() in settings.WEEKDAY_LIST) else False)



def calculate_leave_duration_from_dates(sd,ed,exclude = settings.WEEKDAY_LIST):
	"""
	sd : start date
	ed : end date
	exclude : isoweekdays

	1			Monday

	2			Tuesday

	3			Wednesday

	4			Thursday

	5			Friday

	6			**Saturday

	7			**Sunday
	"""
	if sd and ed:
		dates = list()
		while sd <= ed:
			if not sd.isoweekday() in settings.WEEKDAY_LIST:
				dates.append(sd)
			sd += datetime.timedelta(days = 1)
		return dates
	return


leave_duration = calculate_leave_duration_from_dates



def get_date_object_from_date_str(date_str):
	"""
	date format : 2019-08-14
	year  = 2019
	month = 08
	day   = 14
	"""
	split_date = date_str.split("-")
	y 		   = split_date[0]
	m 		   = split_date[-2]
	d 		   = split_date[2]
	return datetime.date(int(y),int(m),int(d))


date_obj = get_date_object_from_date_str

# def get_isoweekday(date_str):
# 	return get_date_object_from_date_str(date_str).isoweekday()



# def is_weekend(date_str):
# 	return get_isoweekday(date_str) in settings.WEEKDAY_LIST



def pretty_month(date_obj=None):
	if date_obj:
		return date_obj.strftime("%B")
	date_obj = datetime.date.today()
	return date_obj.strftime("%B")



def pretty_year(date_obj=None):
	if date_obj:
		return date_obj.strftime("%Y")
	date_obj = datetime.date.today()
	return date_obj.strftime("%Y")





def day_after_end_date_not_weekend(obj,iso_weekends = [6,7]):
	"""
	How:
	This Function returns a day after the given date,and check if day after does not
	fall on a weekend (weekdays only)
	@:params : date object
	@:return : single date object

	Function (How it works):
	[1] add a day to the date

	[2] check if new date is weekend,if not return new date

	[3] if its weekend: perform step [1] & [2] again (recursive action)

	"""
	try:

		if isinstance(obj,datetime.datetime):
			current_date = obj.date()

		elif isinstance(obj,datetime.date):
			current_date = obj
	except:
		pass

	date_after_day = current_date + datetime.timedelta(days = 1)
	if not date_after_day.isoweekday() in iso_weekends:
		return date_after_day
	return day_after_end_date_not_weekend(date_after_day)
