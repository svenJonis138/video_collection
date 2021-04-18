from urllib import parse
from django.core.exceptions import ValidationError
from django.db import models


class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)

    def save(self, *args, **kwargs):
        """ to override save function and extract video id from the url """
        try:
            # breaking down url components for specific testing
            url_components = parse.urlparse(self.url)
            if url_components.scheme != 'https':
                raise ValidationError(f'Invalid YouTube URL {self.url}')
            if url_components.netloc != 'www.youtube.com':
                raise ValidationError(f'Invalid YouTube URL {self.url}')
            if url_components.path != '/watch':
                raise ValidationError(f'Invalid YouTube URL {self.url}')

            query_string = url_components.query
            if not query_string:
                raise ValidationError(f'Invalid YouTube URL {self.url}')  # raised if there is no query string
            parameters = parse.parse_qs(query_string, strict_parsing=True)  # converts to a dict
            v_parameters_list = parameters.get('v')  # returns none if no key found
            if not v_parameters_list:
                raise ValidationError(f'Invalid YouTube URL, missing parameters {self.url}')
            self.video_id = v_parameters_list[0]  # string
        except ValueError as e:
            raise ValidationError(f'unable to parse URL: {self.url} from {e}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, Video ID: {self.video_id}, Notes: {self.notes[:200]}'
