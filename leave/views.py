import datetime
from .utils import *

from django.core.mail import send_mail #email
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponseRedirect,HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required,user_passes_test

from .utils import leave_duration,date_obj
from .forms import LeaveCreateForm
from absent.models import AbsentPTO
from absent.forms  import  AbsentPTOForm
from account.models import Profile
from .models import *



#simple decorator -> required superuser or admin. # utils.py 
superuser_required = user_passes_test(
	lambda u: u.is_authenticated and u.is_active and u.is_superuser
)



def get_user(request):
	user = request.user
	if not (user.is_authenticated and user.is_active):
		return None
	return user



def is_login_user_superuser(request):
	flag = False
	user = get_user(request)
	if not(user is None):
		if user.is_superuser:
			flag = True
			return flag
		return flag
	return flag



@login_required
def dashboard(request):
	# print(request.user.profile.email)
	flag = None
	user = get_user(request)
	data = dict()
	data['month'] = pretty_month()
	data['year'] = pretty_year()

	current_date = datetime.date.today()
	year = current_date.year
	month = current_date.month
	if not user is None:
		flag = is_login_user_superuser(request)
		if flag:
			#request user is_superuser
			users_profiles = Profile.objects.exclude(user__is_superuser = True)
			pending_leaves = Leave.objects.pending()
			year_approved_leaves = Leave.objects.approved().filter(approved_on__year=year)
			month_approved_leaves = year_approved_leaves.filter(approved_on__month=month)
			data['user_username'] = user
			data['users_profiles'] = users_profiles
			data['pending_leaves'] = pending_leaves 
			data['year_approved_leaves'] = year_approved_leaves
			data['month_approved_leaves'] = month_approved_leaves
			data['notification'] = pending_leaves
			return render(request,'dashboard/dash_index.html',data)
		else:
			#request user is_staff
			user_pending_leaves = Leave.objects.pending().filter(owner__user = user).filter(start_date__year = year) #is_approved = False by admin
			user_year_approved_leaves = Leave.objects.approved().filter(owner__user=user).filter(approved_on__year=year)
			user_month_approved_leaves = user_year_approved_leaves.filter(approved_on__month=month)
			user_unattended_leaves = Leave.objects.unattended_leave().filter(accepted_by = user)#is_accpted = False,leaves user is assigned to take over
			user_assigned_leaves_approved = Leave.objects.approved().filter(accepted_by = user)
			department_pending = Leave.objects.department_pending().filter(owner__department = request.user.profile.department)

			data['department_notifications'] = department_pending #heads of department only
			data['pending_leaves'] = user_pending_leaves
			data['month_approved_leaves'] = user_month_approved_leaves
			data['year_approved_leaves'] = user_year_approved_leaves
			data['assigned_leaves'] = user_assigned_leaves_approved
			data['notification'] = user_unattended_leaves
			return render(request,"dashboard/dash_index.html",data)
	else:
		pass
			
			




@login_required
def create_leave(request):
	login_auth_user = request.user
	user_profile 	= login_auth_user.profile
	message_text = ''
	if login_auth_user.profile.is_exhausted:
		messages.error(request,"You have an exhausted PTO")
	else:
		pass

	if request.method == 'POST':
		form = LeaveCreateForm(login_auth_user,request.POST)
		if form.is_valid():
			leave_instance = form.save(commit=False)
			leave_instance.owner = user_profile
			accepted_by_id = request.POST.get('accepted_by')
			accepted_by = User.objects.filter(id = accepted_by_id).first()
			leave_instance.accepted_by = accepted_by

			leave_instance.save()
			message_text = 'Your PTO is sent to {0} to accept,before head of department and administrator approves.'.format(leave_instance.accepted_by.profile.get_full_name)
			messages.success(request,message_text)
			return redirect('leave:create_leave')
		else:
			message_text = 'Error,please check the start date or end date of PTO.'
			messages.error(request,message_text)
			return redirect('leave:create_leave')
	form = LeaveCreateForm(login_auth_user)#Exclude request.user in form instantiation
	user_recent_sent_leaves = Leave.objects.unattended_leave().filter(owner__user = login_auth_user)
	data = dict()
	data['form'] = form 
	data['recent_leaves'] = user_recent_sent_leaves
	return render(request,'dashboard/leave_create.html',data)





@login_required
def delete_or_edit_leave(request,leave_id):
	#Unattended leaves.
	user = request.user
	leaves = Leave.objects.unattended_leave()
	try:
		leave_obj = leaves.get(id = leave_id)
	except (Leave.DoesNotExist,ValidationError):
		raise Http404("PTO does not exists.")
	leave_owner = leave_obj.owner.user
	if not (leave_owner == user):
		raise PermissionDenied()
	else:
		if 'delete' in request.POST:
			if leave_obj.is_approved is True or leave_obj.is_accepted is True:
				raise PermissionDenied("You can't delete an approved or accepted leave")
			else:
				leave_obj.delete()
		return redirect('leave:create_leave')
	return redirect('leave:create_leave')





@login_required
def leave_edit_by_owner(request,leave_id):
	user = get_object_or_404(User,id = request.user.id)
	leave_obj = Leave.objects.unattended_leave().get(id = leave_id)
	# print(leave_obj)
	form = LeaveCreateForm(user,instance=leave_obj)
	if request.method == 'POST':
		form = LeaveCreateForm(user,instance = leave_obj,data = request.POST)
		if form.is_valid():
			instance = form.save(commit = False)
			instance.is_declined = False
			instance.dept_head = None
			instance.head_declined = False
			instance.approved_dept_head = False
			instance.save()
			messages.success(request,'PTO is successfully updated.')
			return redirect(reverse('leave:edit_leave_by_owner',kwargs={'leave_id':leave_obj.id}))
		else:
			messages.error(request,'Error updating PTO.')
			return redirect(reverse('leave:edit_leave_by_owner',kwargs={'leave_id':leave_obj.id}))
	data = dict()
	data['form'] = form
	data['leave_obj'] = leave_obj
	return render(request,'dashboard/leave_edit.html',data)






@login_required
def recent_leaves(request):
	data = dict()
	flag = None
	user = get_user(request)
	if not user is None:
		flag = is_login_user_superuser(request)
		if flag:
			leaves_approved = Leave.objects.approved()#NOTE: TODO filter in current year 
			data['leaves_approved'] = leaves_approved

		else:
			#staff view - False
			leaves_approved = Leave.objects.approved().filter(owner__user = user)#NOTE: TODO filter in current year
			data['leaves_approved'] = leaves_approved
	return render(request,'dashboard/recent_leaves.html',data)






@login_required
def admin_pending_leave(request,leave_id):
	
	if not (request.user.is_superuser and request.user.is_staff):
		raise PermissionDenied()

	data = dict()
	Leaves = Leave.objects.pending()
	leave_obj = get_object_or_404(Leaves,id = leave_id)
	leave_user_profile = leave_obj.owner
	days_req = leave_obj.leave_days_count()
	if request.method == "POST":
		if 'approve' in request.POST:
			if leave_user_profile.assign_days >= days_req:
				currents_leave_days = leave_user_profile.assign_days - days_req
				leave_user_profile.assign_days = currents_leave_days
				leave_user_profile.save()
				leave_obj.is_approved = True
				leave_obj.approved_by = request.user
				leave_obj.approved_on = timezone.now()
				leave_obj.status = APPROVED
				leave_obj.save()
				message_text = ("successfully approved PTO for {0}".format(leave_obj.owner.user))
				if Leaves.exists():
					messages.success(request,message_text)
					return redirect('leave:staff_pending')
				messages.success(request,message_text)
				return redirect('/')
			else:
				pass

		elif 'cancel' in request.POST:
			leave_obj.delete()
			message_text = ("{0} PTO has been cancel".format(leave_obj.owner.user))
			if Leaves.exists():
				messages.error(request,message_text)
				return redirect('leave:staff_pending')
			messages.error(request,message_text)
			return redirect('/')
	# passing leave object as a GET request.
	data['leave_obj'] = leave_obj
	return render(request,'dashboard/leave_approval_detail.html',data)




@login_required
def pending_leaves_by_department(request,leave_id):
	"""
	Only Heads of Department Can See This and Approve.
	"""
	department_pending = Leave.objects.department_pending().filter(owner__department = request.user.profile.department)
	leave_obj = get_object_or_404(department_pending,id = leave_id)	

	if request.method == 'POST':
		if 'approve' in request.POST:
			# print("approved leave")
			leave_obj.approved_dept_head = True
			leave_obj.dept_head = request.user
			leave_obj.save()
			messages.success(request,"PTO has been approved for {0}".format(leave_obj.owner.get_full_name))
			return redirect('/')
		elif 'decline' in request.POST:
			# print("decline by head.")
			leave_obj.head_declined = True
			leave_obj.dept_head 	= request.user
			leave_obj.is_accepted 	= False
			leave_obj.accepted_by 	= None
			leave_obj.save()
		return redirect('/')
	# print(leave_obj)
	c = {'leave_obj':leave_obj}
	return render(request,'dashboard/heads_approve_leaves.html',c)





@login_required
def assigned_duty_leaves(request):
	#staff only view
	data = dict()
	if not request.user.is_active:
		return redirect(settings.LOGIN_URL)
	if request.user.is_superuser and request.user.is_authenticated:
		return redirect('{0}?next={1}'.format(settings.LOGIN_URL, request.path))
	else:
		user = request.user
		assigned_leaves = Leave.objects.approved().filter(accepted_by = user)
		data['assigned_leaves'] = assigned_leaves
	return render(request,'dashboard/duty_assigned.html',data)





@login_required
def pending_leaves(request):
	#Both staff and admin.
	data = dict()
	user = get_user(request)
	if not (request.user.is_active):
		#login_required thats not check for active users
		return redirect(settings.LOGIN_URL)
	flag = is_login_user_superuser(request)
	if flag:
		#admin
		all_pending = Leave.objects.pending() #TODO -> Filter by year
		data['pending_leaves'] = all_pending
	else:
		#staff
		all_pending = Leave.objects.pending() #TODO -> Filter by year -> set it at managers.py file
		current_user_pending  = all_pending.filter(owner__user = user)
		data['pending_leaves'] = current_user_pending
	return render(request,'dashboard/pending_leaves.html',data)





@login_required
def unattended_leave_detail(request,leave_id):
	data = dict()
	if request.user.is_superuser:
		return redirect('{0}?next={1}'.format(settings.LOGIN_URL, request.path))
	try:
		leave_obj = Leave.objects.unattended_leave().get(id = leave_id)
	except (Leave.DoesNotExist,ValidationError):
		raise Http404("Requested PTO does not exists.")
	data['leave_obj'] = leave_obj
	return render(request,'dashboard/unattended_leave_detail.html',data)





#accept or decline leave by assigned user.
def unattended_leave_actions(request,leave_id):
	leave_objs = Leave.objects.unattended_leave()
	leave_obj  = get_object_or_404(leave_objs,id = leave_id)
	if 'accept' in request.POST:
		leave_obj.is_accepted = True
		owner = leave_obj.owner.get_full_name
		messages.success(request,"Thank you for accepting {0} PTO duties.".format(owner))
		leave_obj.save()
	if 'decline' in request.POST:
		leave_obj.is_declined = True #new
		leave_obj.is_accepted = False
		leave_obj.accepted_by = None #assign leave to None.
		leave_obj.save()
		messages.error(request,"You decline {0} PTO duties.".format(leave_obj.owner))
		# print('you declined PTO')
	return redirect('/')




@transaction.atomic
@superuser_required
def absent_deduction_days(request):

	form = AbsentPTOForm()

	if request.method == 'POST':
		form = AbsentPTOForm(data = request.POST)
		# print(user_profile,deduction)
		if form.is_valid():
			instance = form.save(commit = False)
			user_profile_id    = request.POST.get('user_profile')
			deduction      	   = request.POST.get('deduction')
			# print(deduction)
			profile_instance = get_object_or_404(Profile,id = int(user_profile_id))
			if int(profile_instance.assign_days) >= int(deduction):
				new_value = int(profile_instance.assign_days) - int(deduction)
				# print(new_value)
				profile_instance.assign_days = new_value
				profile_instance.save()
				messages.success(request,"{0} day(s) Deducted from {1} PTO days".format(deduction,profile_instance.get_full_name))
			else:
				messages.error(request,"Error,Deducting Days is more than Remaining PTO days.")
		else:
			messages.error(request,"Invalid data,try again")
		return redirect('leave:deduction')
	return render(request,'dashboard/leave_deduction.html',{'form':form})