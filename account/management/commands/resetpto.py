from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand



User = get_user_model()

def user_profiles():

	users = User.objects.all()

	count = 0 
	if users:
		try:
			for user in users:
				user.profile.assign_days = settings.DEFAULT_LEAVE_DAYS
				user.profile.save()
				user.save()#not necessary,but just save it
				count += 1
			print("{0} user profiles reset".format(count))
		except:
			pass
	else:
		print("No profiles can be found.")



class Command(BaseCommand):
	help = 'reset user profile in db.'
	# @use : python manage.py reset_pto_days


	def handle(self,*args,**kwargs):
		user_profiles()

