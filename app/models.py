from django.db import models
from django.contrib.auth.models import User

class SystemUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    associated_respeaker_token = models.CharField(max_length = 32, blank=True, null = True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class AudioFile(models.Model):
    file = models.FileField(blank=True, null=True, upload_to='uploads/')
    file_name = models.CharField(max_length = 120)
    size = models.CharField(max_length = 10)
    duration = models.CharField(max_length = 10)
    user = models.ForeignKey(SystemUser, on_delete = models.CASCADE, null=True)
    def __str__(self):
        return self.file_name



class Speaker(models.Model): 
    first_name = models.CharField(max_length = 30, null = False, blank = False)
    last_name = models.CharField(max_length = 30, null = False, blank = False)
    user = models.ForeignKey(SystemUser, on_delete = models.CASCADE)
    voice_sample = models.OneToOneField(AudioFile, on_delete = models.SET_NULL, null = True)
    embeddings = models.TextField(blank=True, null = True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Meeting(models.Model):
    name = models.CharField(max_length = 128)
    date_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(SystemUser, on_delete = models.CASCADE)
    audio_file = models.ForeignKey(AudioFile, on_delete = models.SET_NULL, null = True)
    speakers = models.ManyToManyField(Speaker)
    transcript_file = models.TextField(blank=True, null = True)
    summary_file = models.TextField(blank=True, null = True)

    def __str__(self):
        return self.name




