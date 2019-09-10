import uuid
import datetime

from django.utils import timezone
from django.db import models
from django.conf import settings
from .utils import  (TimeStamp,
					calculate_leave_duration_from_dates,
					is_not_weekday,
					day_after_end_date_not_weekend)

from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.contrib.auth.models import User

from account.models import Profile
from .managers import LeaveManager


PENDING  = 'Pending'
APPROVED = 'Approved'
UNAPPROVED = 'Unapproved'
DISCARD  = 'Discarded'



SICK              = 'sick'
VACATION 		  = 'vacation'
END_OF_EMPLOYMENT = 'endofemployment'
MATERNITY_LEAVE   = 'maternity'

LEAVE_TYPE = (
(SICK,'Sick'),
(VACATION,'Vacation'),
(END_OF_EMPLOYMENT,'End of Employment'),
(MATERNITY_LEAVE,'Maternity'),
)





def token():
	return str(uuid.uuid4())


class Leave(TimeStamp):
	"""
	Model : Leave Model
	
	"""
	id 					= models.UUIDField(primary_key=True, default=token, editable=False,unique=True)
	owner				= models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='leaves')
	start_date 			= models.DateField(null=False,blank=False)
	end_date			= models.DateField(null=False,blank=False)
	leave_type  		= models.CharField(choices=LEAVE_TYPE,max_length=30,default=SICK,null=True,blank=False)
	reason 				= models.TextField(max_length=250,null=False,blank=False)
	duty				= models.TextField(max_length=600,null=False,blank=False)
	status				= models.CharField(max_length=15,default=PENDING)
	
	is_approved 		= models.BooleanField(default=False)
	approved_by 		= models.ForeignKey(User,on_delete=models.PROTECT,related_name='to_approve_leaves',null=True,blank=True)
	approved_on 		= models.DateTimeField(null=True,blank=True)


	# Department Head
	approved_dept_head 	= models.BooleanField(default=False)
	dept_head 			= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	head_declined       = models.BooleanField(default=False)

	is_declined			= models.BooleanField(default=False)
	is_accepted 		= models.BooleanField(default=False)
	accepted_by 		= models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=False,related_name='leaves_to')
	report_to			= models.CharField(max_length=250,blank=True,null=True)


	objects = LeaveManager()


	def __str__(self):
		if self.owner:
			return ("({0}) applied for ({1}) leave ".format(self.owner.user.username,self.leave_type))



	class Meta:
		verbose_name  		= 'Leave'
		verbose_name_plural = 'Leaves'
		ordering			= ['-created',]



	def save(self,*args,**kwargs):
		if self.owner.user == self.approved_by:
			raise ValidationError("You can't approve your own leave.")
		if self.owner.user == self.accepted_by:
			raise ValidationError("You cannot hand over to yourself.")

		return super(Leave,self).save(*args,**kwargs)





	@property
	def pretty_start_date(self):
		return self.start_date.strftime("%d,%B %Y") if self.start_date else datetime.date.today()




	@property
	def pretty_end_date(self):
		return self.end_date.strftime("%d,%B %Y") if self.end_date else None




	@property
	def leave_created_by(self):
		'''
		Method : return leave owner if exists else None
		'''
		return self.owner.user.username if self.owner else None




	@property
	def get_reported_supervisor(self):
		if self.report_to and len(self.report_to) > 1:
			return self.report_to
		



	def leave_days_count(self):
		"""
		Method   : This Method calculates the date difference between two **different dates
		Condition: Accurate result is obtained when weekends,holidays are excluded.
		Return   : integer
		"""
		#NOTE : Validate start_date and end_date in forms.py of ModelForm
		return int(len(calculate_leave_duration_from_dates(self.start_date,self.end_date)))




	@property
	def leave_duration(self):
		return self.leave_days_count()




	@property
	def leave_has_ended(self):
		"""
		Return True if leave date is less(in the past) than current date else false.
		"""
		today = timezone.now().date()
		return bool(True if self.end_date < today else False)




	@property
	def return_leave_date(self):

		end_date = self.end_date
		try:
			leave_return_date = day_after_end_date_not_weekend(end_date)
		except:
			pass
		return leave_return_date



	@property
	def pretty_day_leave_return(self):
		return self.return_leave_date.strftime("%A")
	


	@property
	def is_expired_leave(self):
		current_date = datetime.datetime.now().date()
		end_date = self.end_date
		if end_date < current_date:
			#not expired
			return False
		return True

	















	




