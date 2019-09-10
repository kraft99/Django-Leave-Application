from django import forms
from .models import AbsentPTO
from account.models import Profile

class AbsentPTOForm(forms.ModelForm):

	def __init__(self,*args,**kwargs):
		super(AbsentPTOForm,self).__init__(*args,**kwargs)
		self.fields['user_profile'].queryset = Profile.objects.exclude(user__is_superuser = True)

	class Meta:
		model  = AbsentPTO
		fields = ['user_profile','deduction']