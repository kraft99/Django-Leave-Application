from django import forms
from .models import Department


class DepartmentAddForm(forms.ModelForm):
	name        = forms.CharField(max_length=125,help_text='please don\'t append department to name.',widget=forms.TextInput(attrs={'placeholder':'department name'}))
	description = forms.CharField(max_length=250,required = False,widget=forms.TextInput(attrs={'placeholder':'description of department'}))
	
	class Meta:
		model  = Department
		fields = ['name','description']


	def clean_name(self):# calls on form.is_valid()
		cd = self.cleaned_data
		name = cd['name']
		print(name)
		qry = Department.objects.filter(name__iexact = name)
		if qry.exists():
			raise forms.ValidationError("Department with name exists")
		return name