from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from applications.media_handler import views
# from applications.media_handler.views import progress_view
urlpatterns = [
    url(r'^index/$', login_required(views.IndexView.as_view()),name="index"),
    url(r'^upload-images/$', login_required(views.UploadImagesView.as_view()), name="upload-images"),
    url(r'^training/$', views.TrainView.as_view(), name="training"),
    url(r'^capture-images/$', login_required(views.CaptureView.as_view()), name="capture-images"),
    url(r'^user-detail/(?P<id>\d+)/$', views.UserLogView.as_view(), name="user-log"),
    url(r'^export-data/$', views.export_data, name='export-data'),
    url(r'^$', login_required(views.DashboardView.as_view()), name="dashboard"),

]
