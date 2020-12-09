from django.urls import path
from .views import *

app_name = 'app'

urlpatterns = [
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', user_logout, name='logout'),
    path('upload/', InitiateUpload.as_view(), name = 'file_upload_initiate'),
    path('upload/<int:file_id>/', UploadAudio.as_view(), name = 'file_upload'),
    #path('initiateProcessing/', initiate_processing, name='initiate_processing')
]