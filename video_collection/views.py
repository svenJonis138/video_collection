from django.shortcuts import render, redirect
from .forms import VideoForm, SearchForm
from django.contrib import messages
from .models import Video
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower


def home(request):
    app_name = 'MTV, but like....with Music?'
    return render(request, 'video_collection/home.html', {'app_name': app_name})


def add(request):
    """ function for adding videos """
    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()  # creates new Video object and saves it in db
                return redirect('video_list')
                # messages.info(request, 'New Video Saved!')
            except ValidationError:
                messages.warning(request, 'Not a Valid YouTube URL')
            except IntegrityError:
                messages.warning(request, 'Video already in database')

        messages.warning(request, 'Please check the data you entered.')  # if this runs it is an invalid form
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})
    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})


def video_list(request):
    """ function to populate the list of videos """
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term']
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))
    else:
        search_form = SearchForm()
        videos = Video.objects.order_by(Lower('name'))
    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})

