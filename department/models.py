from django.db import models




class Department(models.Model):

	name 		= models.CharField(max_length = 50,blank = False)
	description = models.CharField(max_length = 120,blank = True,null=True)

	created 	= models.DateTimeField(auto_now_add = True)
	updated		= models.DateTimeField(auto_now = True)


	class Meta:
		ordering = ("-created",)
		verbose_name = 'Department'
		verbose_name_plural = 'Departments'


	def __str__(self):
		return self.name





from django.contrib import admin

admin.site.register(Department)
