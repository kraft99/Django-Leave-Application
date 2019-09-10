import datetime
from django import forms
from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from department.models import Department
from .models import Profile


User = get_user_model()



class LoginForm(forms.Form):
	username = forms.CharField(max_length=250,widget=forms.TextInput(attrs={'placeholder':'eg.anthony'}))
	password = forms.CharField(max_length=250,widget=forms.PasswordInput(attrs={'placeholder':'**********'}))	




class RegisterationForm(UserCreationForm):

	qryset = Department.objects.all()
	department = forms.ModelChoiceField(queryset=qryset,label="Department")
	head	  = forms.BooleanField(label="Is Head of Department",initial=False,required=False,help_text="(tick if new user is head of department)")

	class Meta:
		model  = User
		fields = ["username","department","head"]




class UserEditForm(forms.ModelForm):
	username = forms.CharField(label="username",widget=forms.TextInput())

	class Meta:
		model = User
		fields = ['username']

	def __init__(self,username,*args,**kwargs):
		"""
		This displays the username in form input as disabled.
		forms.py
		self.fields['username'].disabled = True
		self.fields['username'].initial = username
		
		views.py
		UserEditForm(request.user.username)

		edit form
		UserEditForm(request.user.username,instance = request.user)
		"""
		super(UserEditForm,self).__init__(*args,**kwargs)
		self.fields['username'].disabled = True
		self.fields['username'].initial = username





class ProfileEditForm(forms.ModelForm):
	pic 	= forms.FileField(label="Picture",help_text='maximum file upload is 5KB, allowed image extensions;jpg or jpeg,png',required = False,widget=forms.FileInput(attrs={'accept':'image/*'}))
	class Meta:
		model  = Profile
		fields = ['first_name','last_name','email','pic']
		# fields = ['first_name','last_name','email','department','pic']


	def __init__(self,*args,**kwargs):
		super(ProfileEditForm,self).__init__(*args,**kwargs)
		# self.fields['department'].disabled = True


	# @transaction.atomic
	# def save(self):
	# 	instance = super().save(commit=False)
	# 	print("called from edit form")

		


	def clean_pic(self):

		pic = self.cleaned_data['pic']
		allow_extension = ['png','jpg','jpeg']
		extension = pic.name.split('.')[1:]
		if not ''.join(extension).lower() in allow_extension:
			raise forms.ValidationError("File extension not supported")

		#validate size
		return pic

