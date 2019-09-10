from django.urls import path
from .import views


app_name = 'department'

urlpatterns = [
    path('settings/add/',views.department,name='department_add'),
    path('settings/actions/<int:department_id>/',views.department_actions,name='delete_edit'),

]
