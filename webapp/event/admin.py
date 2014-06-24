#from django import forms
from django.contrib import admin
from event.models import Device, Player, Event, Event_Player, Team, Person, Team_Coach

admin.site.register(Device)
admin.site.register(Player)
admin.site.register(Event)
admin.site.register(Event_Player)
admin.site.register(Team_Coach)


class PlayerTeamInline(admin.TabularInline):
    model = Player
    readonly_fields = ('guardians', 'person_link')
    fields = ('person_link', 'guardians', 'shirt_number', 'is_active')


class TeamCoachInline(admin.TabularInline):
    model = Team_Coach
    readonly_fields = ('person_link', 'id')
    fields = ('person_link', 'id')
    extra = 0
    verbose_name = "Coach"
    verbose_name_plural = "Coaches"
    extra = 0


class PersonCoachInLine(admin.TabularInline):
    model = Team_Coach
    readonly_fields = ('team_link', 'id')
    fields = ('team_link', 'id')
    extra = 0
    verbose_name = "Coach Role"
    verbose_name_plural = "Coach Roles"
    extra = 0


class TeamAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [PlayerTeamInline, TeamCoachInline]


admin.site.register(Team, TeamAdmin)


class DeviceInline(admin.TabularInline):
	model = Device


class PlayerPersonInline(admin.TabularInline):
    model = Player
    readonly_fields = ('guardians','person', 'team_link')
    fields = ('person', 'team_link', 'guardians', 'shirt_number', 'is_active')
    extra = 0


class PersonAdmin(admin.ModelAdmin):
	list_display = ('username', 'first_name', 'last_name', 'activated', 'last_login', 'date_joined')
	search_fields = ['first_name', 'last_name', 'email']
	fields = (('username', 'password'),
		('activated', 'is_active'),
		('last_login', 'date_joined'),
		('first_name', 'last_name', 'email'), 
		('phone_number', 'dateofbirth'))

	inlines = [DeviceInline, PlayerPersonInline, PersonCoachInLine]


admin.site.register(Person, PersonAdmin)

