from django.contrib import admin
from .models import SystemUser, AudioFile, Speaker, Meeting
# Register your models here.

admin.site.register(SystemUser)
admin.site.register(AudioFile)
admin.site.register(Speaker)
admin.site.register(Meeting)
