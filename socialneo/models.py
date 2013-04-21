from django.db import models
from django.contrib.auth.models import User

from base.models import BaseModel


class NearEarthObject(BaseModel):

    discovered_by = models.ForeignKey(User, null=False)

    name = models.CharField(max_length=100)
    discovery_date = models.DateField()
    right_ascension_hours = models.FloatField()
    right_ascension_minutes = models.FloatField()
    right_ascension_seconds = models.FloatField()
    declination_hours = models.FloatField()
    declination_minutes = models.FloatField()
    declination_seconds = models.FloatField()
    magnitude = models.FloatField()
    arc = models.FloatField()
    nominal_h = models.FloatField()

    desirability = models.IntegerField(default=0)
    num_observations = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=255, null=True, blank=True)
    media = models.FileField(upload_to='neo_media')

    HOUR_DEGREES = 360/24
    MINUTES_DEGREES = HOUR_DEGREES/60
    SECONDS_DEGREES = MINUTES_DEGREES/60

    @property
    def right_ascension_degrees(self):
        degrees = self.HOUR_DEGREES * right_ascension_hours + \
                  self.MINUTES_DEGREES * right_ascension_minutes + \
                  self.SECONDS_DEGREES * right_ascension_seconds

    @property
    def declination_degrees(self):
        degrees = self.HOUR_DEGREES * declination_hours + \
                  self.MINUTES_DEGREES * declination_minutes + \
                  self.SECONDS_DEGREES * declination_seconds


class Observation(BaseModel):
    neo = models.ForeignKey(NearEarthObject)
    observer = models.ForeignKey(User)
    observation_date = models.DateField()

    class Meta:
        unique_together = ('neo', 'observer')
