from django.urls import path
# from django.contrib.auth import views as auth_views
from .import views



app_name='account'

urlpatterns = [
    path('', views.account_login,name='login'),
    path('dashboard/account/register/',views.account_signup,name='register'),
    path('dashboard/account/logout/',views.account_logout,name='logout'),
    path('dashboard/account/users/all/',views.users,name='users'),
    path('dashboard/account/user/<str:username>/delete/',views.delete_user,name='delete_user'),
    path('dashboard/account/profile/view/',views.profile_view,name='profile_view'),
    path('dashboard/account/profile/<str:username>/',views.admin_view_users_profile,name="staff_profile_view"),
    path('dashboard/account/password-change/',views.change_password,name='password_change'),
 #    # Reset Password Routes.
 #    path('password-reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
	# path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
	# path('password-reset/confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
	# path('password-reset/complete/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
  
]

