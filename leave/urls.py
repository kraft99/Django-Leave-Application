from django.urls import path
from . import views



app_name = 'leave'

urlpatterns = [
    path('', views.dashboard,name='dashboard'),
   	path('leave/apply/',views.create_leave,name='create_leave'),
    path('leave/edit/<str:leave_id>/',views.leave_edit_by_owner,name='edit_leave_by_owner'),
   	path('leave/delete/<str:leave_id>/',views.delete_or_edit_leave,name='edit_delete_leave'),
   	path('leaves/recent/',views.recent_leaves,name='recent_leaves'),
   	path('leaves/assign/approved/all/',views.assigned_duty_leaves,name='assign_duty_leaves'),
   	path('leaves/pending/all/',views.pending_leaves,name='staff_pending'),
    path('leaves/pending/detail/<str:leave_id>',views.admin_pending_leave,name='pending_leave'),
    path('leaves/department/pending/<str:leave_id>/',views.pending_leaves_by_department,name="pending_dept_leave"),
   	path('leaves/unattended/detail/<str:leave_id>',views.unattended_leave_detail,name='unattended'),
   	path('leaves/unattended/action/<str:leave_id>',views.unattended_leave_actions,name='leave_action'),
    path('leaves/deduction/absent/',views.absent_deduction_days,name='deduction'),#new line
  
]
