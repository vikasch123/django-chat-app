from django.contrib import admin
from django.urls import path, include, re_path
from fundooapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Home page and sign-up views
    path('', views.index, name='index'),
    path('signup/', views.Signup, name='signup'),
    path('sign_in/', views.login_u, name='sign_in'),

    # Account activation URL (use re_path for regex)
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.activate, name='activate'),

    # Chat app URLs
    path('chat/', include('chat.urls')),

    # Django Auth URLs (includes login, logout, password reset)
    path('accounts/', include('django.contrib.auth.urls')),  # This will include login, logout, password reset etc.

    # Password reset views (if needed explicitly)
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
