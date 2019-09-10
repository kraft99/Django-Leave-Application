import datetime
from django.db.models import Q
from django.db import models
from django.contrib.auth.models import User


# Status Constants
PENDING  = 'Pending'
APPROVED = 'Approved'
UNAPPROVED = 'Unapproved'
DISCARD  = 'Discarded'




class LeaveQuerySet(models.QuerySet):

	def pending(self):
		"""
		Admin .only

		Leave is visible only when its accepted by the handing over person,
		only then can it be a pending leave.
		Condition:(Inclusive)
		[1] is_accepted = True
		[2] status = PENDING
		[3] is_approved = False
		[4] approved_on__isnull=True ie.Empty

   (new)[5] approve_by_dept_head = True
		"""
		return self.filter(Q(is_accepted = True) & Q(status = PENDING) & Q(is_approved = False) & Q(approved_on__isnull=True) & Q(approved_dept_head = True))



	def department_pending(self):
		"""
		Condition:(Inclusive)
		[1] is_accepted = True
		[2] status = PENDING
		[3] is_approved = False (By admin)

		"""
		return self.filter(Q(is_accepted = True) & Q(status = PENDING) & Q(is_approved = False) & Q(approved_on__isnull=True) & Q(approved_dept_head = False))





	def approved(self):
		"""
		Admin.only 

		Leaves that are approved by admin.
		Condition:(Inclusive)
		is_approved = True
		approved_on__isnull=False ie. not Empty
		status 		= APPROVED
		is_accepted = True
		(new)approve_by_dept_head = True
		"""
		return self.filter(Q(is_approved = True) & Q(approved_on__isnull=False) & Q(status = APPROVED) & Q(is_accepted = True) & Q(approved_dept_head = True))




	def approved_leaves_in_a_month(self,month,year):
		"""
		Leaves that a approved in a current month -> search query method.
		"""
		pass




	def unattended_leave(self):
		"""
		All leaves that are only accepted = False 
		"""
		return self.filter(is_accepted = False)




	def assign_to_unaccepted(self,user):
		"""
		Queryset returns all the leaves assigned to a given user to take over (NOT ACCEPTED),staff & admin
		use as a notification to assign_user
		"""
		return self.filter(Q(accepted_by = user) & Q(is_accepted = False))




	def assign_to_accepted(self,user):
		"""
		Queryset returns all the leaves assigned to a given user to take over (ACCEPTED),staff & admin
		"""
		return self.filter(Q(accepted_by = user) & Q(is_accepted = True))




class LeaveManager(models.Manager):

	def get_queryset(self):
		return LeaveQuerySet(self.model,using=self._db) #important



	def pending(self):
		"""
		Example: Leave.objects.pending()
		Extra : Leave.objects.pending().[filter(),first().last().count().select_related etc.]
		"""
		return self.get_queryset().pending()


	def department_pending(self):
		"""
		Only Heads of Department
		Example: Leave.objects.department_pending()
		Extra : Leave.objects.department_pending().[filter(),first().last().count().select_related etc.]
		"""
		return self.get_queryset().department_pending()


	def approved(self):
		"""
		Example: Leave.objects.approved()
		"""
		return self.get_queryset().approved()


	def unattended_leave(self):
		"""
		All leaves that are submitted but are not accepted by assigned user
		"""
		return self.get_queryset().unattended_leave()







