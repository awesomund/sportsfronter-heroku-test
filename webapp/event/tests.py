#coding: utf8
from django.test import TestCase
from django.http import HttpRequest
from event.views import save_event, create_event, delete_event, update_event, rsvp
from event.models import Team, Event, Person, Event_Player, Player, Team_Coach

import json

class EventTestCase(TestCase):

	def setUp(self):
		self.team = Team.objects.create(name="Team 1")
		self.user = Person.objects.create(username="user", password="password")
		Team_Coach(person=self.user, team=self.team).save()

		self.event_input_data = {
		  'title': 'test-created event',
		  'date': '1999-01-01',
		  'meetup_time': '17' + ":" +'30',
		  'start_time': '18'+ ":" + '00',
		  'location': 'the place to be',
		  'info': 'there will also be food!',
		  'opponent': 'the opponents',
		  'attendees': [

						{
						 "phone_number": None,
						 "dateOfBirth": "03.01.55",
						 "first_name": "Osmund",
						 "last_name": "Gmail",
						 "shirt_number": None,
						 "guardians": [],
						 "id": 3,
						 "email": "osmundmaheswaran@gmail.com"
						 },

						{
						 "phone_number": None,
						 "dateOfBirth": "30.09.13",
						 "first_name": "Osmund",
						 "last_name": "Hotmail",
						 "shirt_number": None,
						 "guardians": [{"phone_number": None, "name": "Osmund", "email": "osmundmaheswaran@gmail.com"}],
						 "id": 2,
						 "email": "osmund87@hotmail.com"
						 },

						{
						 "phone_number": None,
						 "dateOfBirth": "30.09.13",
						 "first_name": "Osmund",
						 "last_name": "Iterate",
						 "shirt_number": 1,
						 "guardians": [{"phone_number": None, "name": "Osmund", "email": "osmundmaheswaran@gmail.com"}],
						 "id": 1,
						 "email": "osmund@iterate.no",
						 },
						],

		  'notInvited': None,
		  'team': 1,
		  'event_id': 1,
		  'send_update': False,

		  }


	def test_successfully_save_new_event_without_sending_invitations_and_return_correct_response(self):

		self.assertFalse(Event.objects.filter(pk=1))

		request = HttpRequest()
		request.method = 'POST'
		request._body = json.dumps(self.event_input_data)

		http_response = save_event(request)
		response_data = json.loads(http_response.content)

		self.assertTrue(Event.objects.filter(pk=1))
		self.assertEquals(1, response_data['event_id'])


	def test_successfully_create_event_and_return_correct_response(self):
		
		self.assertFalse(Event.objects.filter(pk=1))

		request = HttpRequest()
		request.method = 'POST'
		request._body = json.dumps(self.event_input_data)

		http_response = create_event(request)
		response_data = json.loads(http_response.content)

		self.assertTrue(Event.objects.filter(pk=1))
		self.assertEquals(1, response_data['event_id'])

	def test_successfully_deleting_event_and_return_correct_response(self):
		Event.objects.create(title="title", info="info", start_datetime="1999-12-12 10:10", meetup_datetime="1999-12-12 15:10", 
					  location="place", team=self.team, opponent="opponent")

		self.assertTrue(Event.objects.filter(pk=1))

		request = HttpRequest()
		request.method = 'POST'
		request._body = json.dumps({'event_id': 1})

		http_response = delete_event(request)
		response_data = json.loads(http_response.content)

		self.assertFalse(Event.objects.filter(pk=1))
		self.assertEquals({}, response_data)


	def test_successfully_updating_existing_event_and_return_correct_response(self):

		event = Event.objects.create(title="title", info="info", start_datetime="1999-12-12 15:10", meetup_datetime="1999-12-12 14:10", 
					  location="place", team=self.team, opponent="opponent")

		self.assertEquals(1, event.pk)
		self.assertEquals(1, event.id)
		self.assertEquals(1, self.event_input_data['event_id'])

		request = HttpRequest()
		request.user = self.user
		request.method = 'POST'
		request._body = json.dumps(self.event_input_data)

		http_response = update_event(request)
		response_data = json.loads(http_response.content)

		self.assertEquals(200, response_data['status'])

		event = Event.objects.get(id=1)

		self.assertEquals(event.team.name, "Team 1")
		self.assertNotEquals(event.info, "info")
		self.assertNotEquals(event.start_datetime.strftime("%Y-%m-%d %H:%M"), "1999-12-12 15:10")
		self.assertNotEquals(event.meetup_datetime.strftime("%Y-%m-%d %H:%M"), "1999-12-12 14:10")
		self.assertNotEquals(event.location, "place")

		self.assertEquals(event.info, "there will also be food!")
		self.assertEquals(event.start_datetime.strftime("%Y-%m-%d %H:%M"), "1999-01-01 18:00")
		self.assertEquals(event.meetup_datetime.strftime("%Y-%m-%d %H:%M"), "1999-01-01 17:30")
		self.assertEquals(event.location, "the place to be")


	def test_that_player_successfully_rsvps_to_event_and_returns_correct_response(self):

		player_person = Person.objects.create(username="player@person.com", password="password", first_name="Roan", last_name="Joan")
		player = Player.objects.create(person=player_person, team=self.team)
		event = Event.objects.create(title="title", info="info", start_datetime="1999-12-12 15:10", meetup_datetime="1999-12-12 14:10", 
						  location="place", team=self.team, opponent="opponent")
		event_player = Event_Player.objects.create(player=player, event_id=event.id, answer=5, sent=True)

		input_data = {"event_player_id": event_player.id, "answer": 1, "comment": "dette er en kommentar"}
		request = HttpRequest()
		request.method = 'POST'
		request._body = json.dumps(input_data)

		http_response = rsvp(request)
		response_data = json.loads(http_response.content)

		event_player = Event_Player.objects.get(player=player, event_id=event.id)

		self.assertEquals(1, event_player.answer)
		self.assertEquals("dette er en kommentar", event_player.comment)

		self.assertEquals(1, response_data['answer'])
		self.assertEquals("dette er en kommentar", response_data['comment'])
		self.assertTrue(response_data['attendees'])








