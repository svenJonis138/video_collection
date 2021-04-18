from django import forms
from .models import Video


class VideoForm(forms.ModelForm):  # for adding videos
    class Meta:
        model = Video
        fields = ['name', 'url', 'notes']


class SearchForm(forms.Form):  # for searching videos
    search_term = forms.CharField()
