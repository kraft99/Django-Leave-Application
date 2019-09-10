from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views


# media(uploaded files by user eg.pictures,files) & static files routes-settings
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('account.urls',namespace='account')),
    path('dashboard/', include('leave.urls',namespace='leave')),
    path('department/', include('department.urls',namespace='department')),
    # Reset Password Routes.
    path('account/password-reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
	path('account/password-reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
	path('account/password-reset/confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
	path('account/password-reset/complete/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
  
  
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

