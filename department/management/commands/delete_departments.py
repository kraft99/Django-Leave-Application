from django.core.management.base import BaseCommand
from ...models import Department


def delete_departments():

	count = 0
	for department in Department.objects.all():
		department.delete()
		count += 1
	print("{0} departments deleted".format(count))





class Command(BaseCommand):
	help = 'This command deletes all departments in the database.'
	#@use: python manage.py delete_departments

	def handle(self,*args,**kwargs):
		delete_departments()
	

