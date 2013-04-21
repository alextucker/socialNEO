import json
import urllib
import requests

from datetime import datetime

from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from socialneo.models import NearEarthObject, Observation
from socialneo.forms import NeoSubmitForm

from social_auth.models import UserSocialAuth


class AuthMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AuthMixin, self).dispatch(*args, **kwargs)

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self):
        context = {}
        context['settings'] = settings
        return context


class ProfileView(TemplateView):
    template_name = "profile.html"

    def get_context_data(self, user):
        context = {}
        context['profile_user'] = User.objects.get(username=user)
        context['neos'] = NearEarthObject.objects.filter(discovered_by=context['profile_user'])
        context['settings'] = settings
        return context


class MyProfileView(ProfileView):

    def get_context_data(self):
        context = {}
        context['neos'] = NearEarthObject.objects.filter(discovered_by=self.request.user)
        context['profile_user'] = self.request.user
        context['settings'] = settings
        return context



class SubmitView(AuthMixin, TemplateView):
    template_name = "submit.html"

    def get_context_data(self):
        context = {}
        context['settings'] = settings
        return context

    def _parse_time(self, value):

        value = value.split(' ')
        hours = value[0]

        value = value[1].split('.')
        minutes = value[0]
        seconds = value[1]

        return hours, minutes, seconds

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied

        form = NeoSubmitForm(request.POST, request.FILES)

        if form.is_valid():

            declination = self._parse_time(form.cleaned_data.pop('declination'))
            right_ascension = self._parse_time(form.cleaned_data.pop('right_ascension'))


            extra_data = {
                'discovered_by': request.user,
                'right_ascension_hours': right_ascension[0],
                'right_ascension_minutes': right_ascension[1],
                'right_ascension_seconds': right_ascension[2],
                'declination_hours': declination[0],
                'declination_minutes': declination[1],
                'declination_seconds': declination[2],
            }

            form.cleaned_data.update(extra_data)

            neo = NearEarthObject(**form.cleaned_data)
            neo.save()

            # Facebook open graph action

            social_user = UserSocialAuth.objects.get(user=request.user)

            if 'access_token' not in social_user.tokens:
                social_user.refresh_token()

            access_token = social_user.tokens['access_token']

            neo_url = "http://"
            neo_url += request.META['HTTP_HOST']
            neo_url += reverse('neo_item', kwargs={'neo_id': neo.id})

            data = {
                'access_token': access_token,
                'METHOD': 'POST',
                'near_earth_object': neo_url
            }

            data = urllib.urlencode(data)

            response = requests.post('https://graph.facebook.com/me/socialneo:discover?' + data)

            return redirect('/neo/' + str(neo.id))
        else:
            return render_to_response(self.template_name, {"message": "failed to create"})


class NEOListView(TemplateView):
    template_name = "neo/list.html"

    def get_context_data(self):
        context = {}
        context['settings'] = settings
        context['neos'] = NearEarthObject.objects.order_by('-created_at')[:20]

        trending_list = Observation.objects.values_list('neo__id', flat=True).annotate(count=Count('neo__id')).order_by('-count')[:5]
        context['trending'] = NearEarthObject.objects.filter(id__in=list(trending_list))

        return context


class NEOItemView(TemplateView):
    template_name = "neo/item.html"

    def get_context_data(self, neo_id):
        context = {}
        context['r'] = self.request
        context['settings'] = settings
        context['neo'] = NearEarthObject.objects.get(pk=neo_id)
        context['neo_image'] = NearEarthObject.objects.get(pk=neo_id).media.url.split('?')[0]
        return context

class NEOItemObserveView(AuthMixin, TemplateView):
    template_name = "neo/item.html"

    def get(self, request, *args, **kwargs):
        neo = NearEarthObject.objects.get(pk=self.kwargs.get('neo_id'))

        if Observation.objects.filter(neo=neo, observer=request.user).count() > 0:
            return redirect('/neo/' + self.kwargs.get('neo_id'))

        observation = Observation(neo=neo, observer=request.user, observation_date=datetime.now())
        observation.save()

        # Facebook open graph action

        social_user = UserSocialAuth.objects.get(user=neo.discovered_by)

        if 'access_token' not in social_user.tokens:
            social_user.refresh_token()

        access_token = social_user.tokens['access_token']

        neo_url = "http://"
        neo_url += request.META['HTTP_HOST']
        neo_url += reverse('neo_item', kwargs={'neo_id': neo.id})

        data = {
            'access_token': access_token,
            'METHOD': 'POST',
            'near_earth_object': neo_url
        }

        data = urllib.urlencode(data)

        response = requests.post('https://graph.facebook.com/me/socialneo:observe?' + data)

        return redirect('/neo/' + self.kwargs.get('neo_id'))

