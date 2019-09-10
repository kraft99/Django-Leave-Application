
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect,HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,user_passes_test

from account.models import Profile
from .models import Department
from .forms import DepartmentAddForm



#simple decorator -> required superuser or admin.
#can use it for active_user_login_required (default fails to check if user is active.)
superuser_required = user_passes_test(
	lambda u: u.is_authenticated and u.is_active and u.is_superuser
)


@login_required
@superuser_required
def department(request):
	
	form = DepartmentAddForm()
	if request.method == 'POST':
		form = DepartmentAddForm(data = request.POST)
		message_text = ''
		if form.is_valid():
			instance = form.save(commit = False)
			department_name = request.POST.get('name').upper()
			instance.save()
			message_text = 'Successfully created {0} department'.format(department_name)
			messages.success(request,message_text)
		else:
			message_text = 'Failed to create department'
			messages.error(request,message_text)
		return redirect('department:department_add')
	data = dict()
	departments = Department.objects.all()
	# print(departments)
	data['form'] = form
	data['departments'] = departments
	return render(request,'department/add.html',data)




@login_required
@superuser_required
def department_actions(request,department_id):
	department = get_object_or_404(Department,id = department_id)
	profile_with_dept = Profile.objects.filter(department = department.name)#check if any profile exists with department name
	if request.method == 'POST':
		message_text = ''
		if 'delete' in request.POST:
			if profile_with_dept.exists():
				# print("{0} Department is tagged to users".format(department.name))
				message_text = "{0} Department is already tagged to users".format(department.name)
				messages.error(request,message_text)
			else:
				department.delete()
				message_text = '{} Department has been deleted'.format(department.name)
				messages.success(request,message_text)
		elif 'edit' in request.POST:
			pass

	return redirect('department:department_add')

