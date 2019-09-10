import os
from django.db import models
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.db.models.signals import post_save,pre_save,post_delete
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.dispatch import receiver


DEFAULT_IMAGE_PATH = settings.DEFAULT_IMAGE_PATH if settings.DEFAULT_IMAGE_PATH else '/avatar/default_avatar.jpeg'




def pics_location(instance,file_obj):
	import os

	file_ext = file_obj.split('.')[-1]
	file_obj = '{}.{}'.format(instance.user.username,file_ext)
	return os.path.join("dp",file_obj)
	


class Profile(models.Model):

	user 		= models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='profile')
	first_name	= models.CharField(max_length=250,blank=True,null=True)
	last_name	= models.CharField(max_length=250,blank=True,null=True)
	email		= models.EmailField(max_length=250,blank=True,null=True)

	department  = models.CharField(max_length=250,null=True,blank=False) 
	is_head     = models.BooleanField(default = False,null=True,blank=True)

	assign_days = models.PositiveSmallIntegerField(default=settings.DEFAULT_LEAVE_DAYS,blank=True,null=True)
	pic			= models.ImageField(upload_to=pics_location,default='/avatar/default_avatar.jpeg',null=True,blank=True)
	created		= models.DateTimeField(auto_now_add=True,auto_now=False)
	updated 	= models.DateTimeField(auto_now_add=False,auto_now=True)



	def __str__(self):
		if self.first_name and self.last_name:
			return "{0} {1}".format(self.first_name,self.last_name)
		return self.user.username


	@property
	def get_full_name(self):
		if self.first_name and self.last_name:
			return ("{0} {1}".format(self.first_name,self.last_name))
		return ("{0}".format(self.user.username))



	@property
	def get_first_last_name(self):
		if (self.first_name and self.first_name != " ") and (self.last_name and self.last_name != " "):
			return ("{0} {1}".format(self.first_name,self.last_name))
		return





	@property
	def is_exhausted(self):
		"""
		Method: Checks whether a user assign_days  == 0

		@return (boolean): True if leave is 0 else False
		"""

		return bool(True if int(self.assign_days) == 0 else False)





	def can_user_approve_leave(self,leave_instance):
		if not (self.user.is_superuser and self.user.is_authenticated):
			return False
		if leave_instance.owner == self:
			return False
		return True




	@property
	def profile_pic(self):
		if self.pic.url:
			return self.pic.url
		return DEFAULT_IMAGE_PATH



	@property
	def pretty_leave_ratio(self):
		if not self.assign_days == int(settings.DEFAULT_LEAVE_DAYS):
			return ("{0}/{1}".format(self.assign_days,settings.DEFAULT_LEAVE_DAYS))
		return ("{0}".format(self.assign_days))



	@property
	def users_pending_leave(self):
		leaves = self.leaves.filter(is_accepted = True,is_approved=False)
		return  leaves[:1]





#Auto Delete Profile pic after user is deleted.
@receiver(post_delete,sender=Profile)
def auto_delete_pic(sender,instance,**kwargs):
	if instance.pic:
		try:
			if os.path.isfile(instance.pic.path):
				os.remove(instance.pic.path)
		except:
			pass




# Signals 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)




@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()




