#coding: utf8
from django.test import TestCase
from event.models import Player, Person, Team
from management.views import check_username, add_player, remove_from_team, update_player
from django.http import HttpRequest
from event.views import json_response

import json

class UserNameTestCase(TestCase):

	def setUp(self):

		self.guardians = [{"lastName": "Pettersen", "phoneNumber": None, "email": "a@b.com", "firstName": "Fredrik", "id": 4}]


	def test_check_username_returns_None_if_everything_is_ok(self):
		self.assertIsNone(check_username(self.guardians, "player@email.com"))


	def test_check_username_returns_error_message_for_bad_input(self):
		self.assertEquals('Spiller og foresatte må ha forskjellig e-mail.', check_username(self.guardians, "a@b.com"))


class AddOrUpdatePlayerIntegrationTestCase(TestCase):

	def setUp(self):
		self.playerInput = {

					   "shirtNumber": 1,
					   "dateOfBirth": "2013-09-30",
					   "phoneNumber": None,
					   "firstName": "Petter",
					   "lastName": "Fredriksen",
					   "isCoach": False,
					   "guardians": [
					   					{

					   					 "lastName": "Frederico",
					   				  	 "phoneNumber": None,
					   				  	 "email": "new@guardian.com",
					   				  	 "firstName": "Pedro",
					   				  	 "id": 3

					   				  	 }
					   				],
					   	"id": 1,
					   	"email": "new@player.com"
		}


	def test_that_add_player_succeeds_and_returns_correct_response(self):
		request = HttpRequest()
		request.user = Person.objects.create(username="user@user.com", password="user")
		request.method = 'POST'
		request._body = json.dumps(self.playerInput)
		team = Team.objects.create(name="Team")

		http_response = add_player(request, team.id)
		response_data = json.loads(http_response.content)

		self.assertEquals(200, response_data['status'])


	def test_successfully_deleting_a_player_and_returning_correct_response(self):
		person = Person.objects.create(username="a@b.com", password="1234")
		team = Team.objects.create(name="Team")
		player = Player.objects.create(person=person, team=team)

		request = HttpRequest()
		request.user = Person.objects.create(username="user@user.com", password="user")
		request.method = 'GET'

		http_response = remove_from_team(request, player.id)
		response_data = json.loads(http_response.content)

		self.assertEquals("player", response_data['removed'])


	def test_successfully_updating_a_player_and_returning_correct_response(self):
		request = HttpRequest()
		request.user = Person.objects.create(username="user@user.com", password="user")
		request.method = 'POST'
		request._body = json.dumps(self.playerInput)

		person = Person.objects.create(username="a@b.com", password="1234")
		team = Team.objects.create(name="Team")
		player = Player.objects.create(person=person, team=team)

		http_response = update_player(request, player.id)
		response_data = json.loads(http_response.content)

		self.assertEquals(200, response_data['status'])






