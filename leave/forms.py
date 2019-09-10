import datetime
from django.conf import settings
from .import utils
from django.contrib.auth.models import User
from account.models import Profile
from django import forms
from .models import *


class LeaveCreateForm(forms.ModelForm):

	def __init__(self,user_id,*args,**kwargs):
		super(LeaveCreateForm,self).__init__(*args,**kwargs)
		"""
		Line 16 & 17
		List all users in the database excluding superuser & request.user .
		"""
		superuser_id = User.objects.filter(is_superuser = True).first().id
		self.fields['accepted_by'].queryset = User.objects.exclude(id__in = [user_id.id,superuser_id])#exclude login-user(request.user) & superuser in drop-down user list
	qryset = User.objects.all()
	accepted_by = forms.ModelChoiceField(queryset=qryset,label="Assign work to")#work on the list of users
	leave_type = forms.ChoiceField(choices=LEAVE_TYPE,label="Leave Type",required=True,initial=SICK,widget=forms.RadioSelect())
	start_date = forms.DateField(label="Start Date",required=True,help_text="selected date must not be a weekend.")
	end_date = forms.DateField(label="End Date",required=True,help_text="selected date must not be a weekend.")

	class Meta:
		model = Leave
		exclude = ['is_approved','approved_by','approved_on','is_accepted','status','owner','approved_dept_head','dept_head','is_declined','head_declined']


	def clean_end_date(self):
		
		cd = self.cleaned_data
		end_date = cd['end_date']
		start_date = cd['start_date']
		leave_dates = utils.calculate_leave_duration_from_dates(start_date,end_date)
		if len(leave_dates) >= 30:
			raise forms.ValidationError("Leave Days cannot exceed or be equal to 30 day's")
		return end_date





