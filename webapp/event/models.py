from django.db import models
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse


class Team(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def players(self):
        return self.team_player.all()

    def all_coaches_link(self):
        return ['<a href="%s">%s</a>' % (reverse("admin:event_person_change", args = (coach.id,)), coach.first_name + ' ' + coach.last_name) for coach in self.coaches.all()]


class Person(User):
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    dateofbirth = models.DateTimeField(null=True, blank=True)
    coach_roles = models.ManyToManyField(Team, null=True, blank=True, related_name="coaches", through="Team_Coach")
    activated = models.BooleanField(default=False)

    def get_coach_roles(self):
        #return '\n'.join(['<a href="%s">%s</a>' % (reverse("admin:event_team_change", args = (self.coach_role.id,)), self.coach_role.name)] for coach_role in self.coach_roles)
        return [str(coach_role.name) for coach_role in self.coach_roles.all()]

    def __unicode__(self):
        return self.first_name + " " + self.last_name + " (" + self.username + ")"


class Team_Coach(models.Model):
    person = models.ForeignKey(Person)
    team = models.ForeignKey(Team)

    def team_link(self):
        return '<a href="%s">%s</a>' % (reverse("admin:event_team_change", args = (self.team.id,)), self.team.name)

    team_link.allow_tags = True
    team_link.short_description = "Team"

    def person_link(self):
        return '<a href="%s">%s</a>' % (reverse("admin:event_person_change", args = (self.person.id,)), self.person.first_name + " " + self.person.last_name)

    person_link.allow_tags = True
    person_link.short_description = "Person"

    class Meta:
        db_table = 'event_person_coach_roles'
        unique_together = (('person', 'team'))

    def __unicode__(self):
        return self.person.username + " " + self.team.name


class Player(models.Model):
    guardians = models.ManyToManyField(Person, null=True, blank=True, related_name="guardian")
    person = models.ForeignKey(Person)
    team = models.ForeignKey(Team, related_name="team_player")
    shirt_number = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def person_link(self):
        return '<a href="%s">%s</a>' % (reverse("admin:event_person_change", args = (self.person.id,)), self.person.first_name + " " + self.person.last_name)

    person_link.allow_tags = True
    person_link.short_description = "Person"

    def team_link(self):
        return '<a href="%s">%s</a>' % (reverse("admin:event_team_change", args = (self.team.id,)), self.team.name)

    team_link.allow_tags = True
    team_link.short_description = "Team"


    def __unicode__(self):
        return self.person.first_name + " on " + self.team.name


class Event_Group(models.Model):
    title = models.CharField(max_length=512)

    def __unicode__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=512)
    meetup_datetime = models.DateTimeField(null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    last_signup_datetime = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255)
    info = models.TextField(null=True, blank=True)
    team = models.ForeignKey(Team)
    opponent = models.CharField(max_length=255, null=True, blank=True)

    two_day_reminder_sent = models.BooleanField(default=False)
    two_hour_reminder_sent = models.BooleanField(default=False)

    event_group = models.ForeignKey(Event_Group, related_name="events", null=True, blank=True)
    reminder_time = models.IntegerField(null=True, blank=True) #days before event start
    first_reminder_sent = models.BooleanField(default=False)

    uid = models.TextField(null=True, blank=True) #nff

    def __unicode__(self):
        return self.title


class Event_Player(models.Model):
    player = models.ForeignKey(Player)
    event = models.ForeignKey(Event)
    url_hash = models.CharField(max_length=255)
    sent = models.BooleanField()
    seen = models.BooleanField()
    answer = models.IntegerField()
    comment = models.CharField(null=True, blank=True, max_length=255)
    signup_datetime = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return self.event.title + " - " + self.player.person.first_name


class Event_Coach(models.Model):
    person = models.ForeignKey(Person)
    event = models.ForeignKey(Event)
    answer = models.IntegerField()

    def __unicode__(self):
        return self.coach.username + " " + self.event.title


class Device(models.Model):
    owner = models.ForeignKey(Person)
    registration_id = models.CharField(max_length=512)
    device_type = models.CharField(max_length=20)

    def __unicode__(self):
        return self.owner.username
