from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .forms import LoginForm,UserEditForm,ProfileEditForm,RegisterationForm
from department.forms import DepartmentAddForm
from department.models import Department
from .models import Profile


User = get_user_model()


@login_required
def account_signup(request):
	"""
	Admin only view -> create users
	"""
	if not(request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
		raise PermissionDenied("You don't have permission")
	#POST REQUEST
	form = RegisterationForm()
	if request.method == 'POST':
		form = RegisterationForm(data = request.POST)
		mssg = ''
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()#signal sent to create a profile object.
			
			department_id = form.cleaned_data.get("department")
			is_head = form.cleaned_data.get("head")

			username = form.cleaned_data.get("username")
			profile_instance = Profile.objects.filter(user__username = username)[0]
			# print(profile_instance)
			profile_instance.is_head = is_head
			profile_instance.department = department_id.name
			profile_instance.save()
			mssg = "Account created for {0}".format(username)
			messages.success(request,mssg)
			return redirect('account:register')
		else:
			mssg = 'Failed to create account'
			messages.error(request,mssg)
			return redirect('account:register')
	#GET REQUEST
	chop_out_users = User.objects.exclude(id = request.user.id).order_by("-id")[:3]
	all_users_in_db_exclude_admin = User.objects.exclude(id = request.user.id)
	more_users_exist = False
	if all_users_in_db_exclude_admin.count() > chop_out_users.count():
		more_users_exist = True
	context = dict()
	context['form'] = form
	context['users'] = chop_out_users
	context['more_exists'] = more_users_exist
	return render(request,'account/register.html',context)
	




def account_login(request):

	context = dict()
	if request.user.is_authenticated and request.user.is_active:
		return redirect(reverse("leave:dashboard"))
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(username=cd['username'],password=cd['password'])
			if user is not None:
				if user.is_active:
					login(request,user)
					return redirect(reverse("leave:dashboard"))
				else:
					messages.error(request,"Account is disabled")
					return redirect("/")
			else:
				messages.error(request,"Your username or password didn't match.Please try again")
				return redirect("/")
		else:
			messages.error(request,"Your username or password didn't match.Please try again")
			return redirect("/")
	else:
		form = LoginForm()
		context['form'] = form
	return render(request,"account/login.html",context)
		



@transaction.atomic
@login_required
def change_password(request):

	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user_instance = form.save(commit = True)
			update_session_auth_hash(request,user_instance)
			messages.success(request,"password is successfully changed")
			return redirect('account:password_change')#logout user ?
		else:
			messages.error(request,"error changing password,try again")
			return redirect('account:password_change')

	form = PasswordChangeForm(request.user)
	data = dict()
	data['form'] = form
	return render(request,'account/password_change.html',data)




@login_required
def profile_view(request):
	#user_form = UserEditForm(request.user.username)#initialize form with username(READ-ONLY)
	auth_user = request.user
	user_form = UserEditForm(request.user.username,instance = request.user)
	profile_form = ProfileEditForm(instance = request.user.profile)
	if request.method == "POST":
		user_form = UserEditForm(request.user.username,instance = request.user,data = request.POST)
		profile_form = ProfileEditForm(instance=request.user.profile,data=request.POST,files=request.FILES)
		message_txt = ""
		if user_form.is_valid() and profile_form.is_valid():
			instance_user = user_form.save(commit = False)
			instance_profile = profile_form.save(commit = False)
			if request.POST.get('email'):
				auth_user.email = request.POST.get('email') #set email in profile to user.
				auth_user.save() #save user
			instance_profile.save()
			instance_user.save() #re-save user ?
			message_txt = "profile is successfully updated"
			messages.success(request,message_txt)
		else:
			message_txt = "error updating your account"
			messages.error(request,message_txt)
		return redirect(reverse("account:profile_view"))
	profile = Profile.objects.filter(user = request.user).get()
	c = {'profile':profile,'u_form':user_form,'p_form':profile_form}
	return render(request,'account/user_profile_view.html',c)





@login_required
def admin_view_users_profile(request,username):
	if not (request.user.is_superuser and request.user.is_staff):
		raise PermissionDenied()
		
	user = User.objects.filter(username = username).first()
	user_form = UserEditForm(user.username,instance = user)
	profile_form = ProfileEditForm(instance = user.profile)
	if request.method == "POST":
		user_form = UserEditForm(user.username,instance = user,data = request.POST)
		profile_form = ProfileEditForm(instance=user.profile,data=request.POST,files=request.FILES)
		message_txt = ""
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			message_txt = "successfully updated account for {0}".format(username)
			messages.success(request,message_txt)
		else:
			message_txt = "error updating account for {0}".format(username)
			messages.error(request,message_txt)
		return redirect(reverse("account:staff_profile_view",kwargs={'username':username}))
	profile = Profile.objects.filter(user = user).get()
	c = {'profile':profile,'u_form':user_form,'p_form':profile_form}
	return render(request,'account/admin_view_staff_profile.html',c)




@login_required
def delete_user(request,username):
	if not(request.user.is_superuser and request.user.is_staff):
		raise PermissionDenied()
	user = get_object_or_404(User,username = username)
	user.delete()
	messages.success(request,'Account for {0} is deleted'.format(user.username))
	return redirect('account:users')





@login_required
def users(request):
	if not (request.user.is_superuser and request.user.is_staff):
		return redirect('{0}?next={1}'.format(settings.LOGIN_URL, request.path))

	users = User.objects.all()

	qry = request.GET.get('search')
	flag = False
	if qry and len(qry) > 0:
		flag = True
		users = users.filter(Q(username__icontains=qry)).distinct()#TODO:Search in Profile DB would have been better.
	# Paginate
	paginator = Paginator(users,settings.DISPLAY_PER_PAGE)
	page 	  = request.GET.get('page')

	users_list = paginator.get_page(page)
	c = {'users':users_list,'flag':flag}
	return render(request,'account/users.html',c)




def account_logout(request):
	logout(request)
	messages.success(request,"you have successfully logged out")
	return redirect("/")



