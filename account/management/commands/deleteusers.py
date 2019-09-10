from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone



# class Command(BaseCommand):
# 	help =  'Display current time'


# 	def handle(self,*args,**kwargs):
# 		time = timezone.now().strftime("%X")
# 		self.stdout.write("It's now {0}".format(time))

def users_to_delete():
	users = User.objects.all()
	# print("deleted {}".format(users.count()))
	users = User.objects.all()
	if users:
		count = 0
		try:
			for user in users:
				user.delete()
				count += 1
			print("Found and deleted ({0}) user(s)".format(count))
		except:
			print("Error deleting a user")
	else:
		print("No users can be found")



class Command(BaseCommand):
	help = 'clear users account in db.'
	# @use : python manage.py delete_users


	def handle(self,*args,**kwargs):
		users_to_delete()

