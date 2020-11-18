from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    url(r'^signup/$', views.SignUpView.as_view(), name="signup"),
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    url(r'^logout/$', views.LogoutView.as_view(), name="logout"),
    url(r'^delete-user/$', views.DeleteUserView.as_view(), name="delete-user"),
    url(r'^user-encodes/$', views.UserEncodesView.as_view(), name="user-encodes"),
    url(r'^process/$', views.process, name="process"),
    # url(r'^logs/post/$', views.process, name="process"),
    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(),name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
]
