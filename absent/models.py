from django.db import models
from account.models import Profile
# Create your models here.



DEDUCTION = [(i,str(i)) for i in range(1,31)]
#[ range from 1 to 30 inclusive]

class AbsentPTO(models.Model):

	user_profile 	= models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='absent_pto')
	deduction		= models.PositiveSmallIntegerField(choices=DEDUCTION,blank=False,null=True)

	created			= models.DateTimeField(auto_now_add=True)
	updated			= models.DateTimeField(auto_now=True)


	class Meta:
		verbose_name 		= 'AbsentPTO'
		verbose_name_plural = 'AbsentPTOs'
		ordering 			= ('created',)


	def __str__(self):
		return self.user_profile


from django.contrib import admin

admin.site.register(AbsentPTO)