from rest_framework import serializers
from .models import AudioFile


class FileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = AudioFile
        fields = ['id', 'file_name', 'file', 'size', 'duration', 'user']
