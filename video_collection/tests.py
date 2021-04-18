from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django.test import TestCase
from django.urls import reverse

from .models import Video


class TestHomePageMessage(TestCase):

    def test_app_title_message_on_home_page(self):  # tests if the correct message is displayed on the home page
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'MTV')


class TestAddVideos(TestCase):

    def test_add_video(self):

        valid_video = {  # actual video from youtube for testing
            'name': 'japanther',
            'url': 'https://www.youtube.com/watch?v=AnixtQu7HdU',
            'notes': '1-2-3-4 fuck the cops could be an anthem for 2020 or 2021'
        }
        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)
        self.assertTemplateUsed('video_collection/video_list.html')
        self.assertContains(response, 'japanther')
        self.assertContains(response, '1-2-3-4 fuck the cops could be an anthem for 2020 or 2021')
        self.assertContains(response, 'https://www.youtube.com/watch?v=AnixtQu7HdU')

        video_count = Video.objects.count()  # tests that the valid video was added
        self.assertEqual(1, video_count)

        video = Video.objects.first()

        self.assertEqual('japanther', video.name)
        self.assertEqual('1-2-3-4 fuck the cops could be an anthem for 2020 or 2021', video.notes)
        self.assertEqual('https://www.youtube.com/watch?v=AnixtQu7HdU', video.url)
        self.assertEqual('AnixtQu7HdU', video.video_id)

    def test_add_video_invalid_url_not_added(self):
        invalid_video_urls = [
            'https://musicbrainz.org/doc/MusicBrainz_API/Examples',  # invalid urls for testing
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?v=',
            'https://www.youtube.com/'
        ]
        for invalid_url in invalid_video_urls:
            new_video = {
                'name': 'japanther',
                'url': invalid_url,
                'notes': 'some notes would go here'
            }

            response = self.client.post(reverse('add_video'), data=new_video)

            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [message.message for message in messages]
            self.assertIn('Not a Valid YouTube URL', message_texts)
            self.assertIn('Please check the data you entered.', message_texts)

            self.assertContains(response, 'Please check the data you entered')
            self.assertContains(response, 'Not a Valid YouTube URL')

            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    def test_all_videos_displayed_in_correct_order(self):
        v1 = Video.objects.create(name='lol', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='lmfao', notes='example', url='https://www.youtube.com/watch?v=124')
        v3 = Video.objects.create(name='rotgl', notes='example', url='https://www.youtube.com/watch?v=125')
        v4 = Video.objects.create(name='wtf', notes='example', url='https://www.youtube.com/watch?v=126')

        expected_video_order = [v2, v1, v3, v4]
        response = self.client.get(reverse('video_list'))
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_no_video_message(self):
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, 'No Videos')
        self.assertEquals(0, len(videos_in_template))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='blah blah', notes='it was great', url='https://www.youtube.com/watch?v=1138')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='blah blah', notes='it was great', url='https://www.youtube.com/watch?v=1138')
        v2 = Video.objects.create(name='blah', notes='it was not great', url='https://www.youtube.com/watch?v=8311')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '2 videos')


class TestVideoSearch(TestCase):
    def test_video_search_matches(self):
        v1 = Video.objects.create(name='lalala', notes='words', url='https://www.youtube.com/watch?v=138')
        v2 = Video.objects.create(name='blabla', notes='stuff', url='https://www.youtube.com/watch?v=666')
        v3 = Video.objects.create(name='LAla shimirmir', notes='other stuff', url='https://www.youtube.com/watch?v=90210')
        v4 = Video.objects.create(name='zehbetabata', notes='no words', url='https://www.youtube.com/watch?v=404')

        expected_video_order = [v3, v1]
        response = self.client.get(reverse('video_list') + '?search_term=lala')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='lalala', notes='words', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='blabla', notes='stuff', url='https://www.youtube.com/watch?v=666')
        v3 = Video.objects.create(name='LAla shimirmir', notes='other stuff', url='https://www.youtube.com/watch?v=90210')
        v4 = Video.objects.create(name='zehbetabata', notes='no words', url='https://www.youtube.com/watch?v=404')

        expected_video_order = []
        response = self.client.get(reverse('video_list') + '?search_term=YOLO')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No Videos')


class TestVideoModel(TestCase):
    def test_duplicate_video_raises_Integ_error(self):
        v1 = Video.objects.create(name='lalala', notes='words', url='https://www.youtube.com/watch?v=456')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='lalala', notes='words', url='https://www.youtube.com/watch?v=456')

    def test_invalid_urls_raise_validation_error(self):
        invalid_video_urls = [
            'https://musicbrainz.org/doc/MusicBrainz_API/Examples',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?v=',
            'https://www.youtube.com/'
        ]
        for invalid in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='whatever', url=invalid, notes='talk is cheap')
        video_count = Video.objects.count()
        self.assertEqual(0, video_count)

    def test_create_id(self):
        video = Video.objects.create(name='words', url='https://www.youtube.com/watch?v=THX113890210')
        self.assertEqual('THX113890210', video.video_id)

    def test_create_id_valid_url_with_time_parameter(self):
        video = Video.objects.create(name='rutherford b have', url='https://www.youtube.com/watch?v=uIvJGDQJ1iw=11')
        self.assertEqual('uIvJGDQJ1iw=11', video.video_id)

    def test_create_video_notes_optional(self):
        v1 = Video.objects.create(name='words', url='https://www.youtube.com/watch?v=90210')
        v2 = Video.objects.create(name='more words', notes='dear diary...', url='https://www.youtube.com/watch?v=11381')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        self.assertCountEqual(expected_videos, database_videos)
