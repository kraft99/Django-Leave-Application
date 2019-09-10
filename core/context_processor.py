import datetime

def current_year(request):
	now = datetime.date.today()
	return {"current_year":now.year}