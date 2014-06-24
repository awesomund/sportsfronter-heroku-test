# coding: utf8
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from event.models import Player, Team, Person, Event, Event_Player, Team_Coach, Event_Coach
from event.views import json_response, json_error, generate_url_hash
from event.email_utils import send_username_update_mail
from auth.views import get_person_from_request, logout_view

import json
import datetime
import logging
import random
import requests
import re

logger = logging.getLogger("sportsfronter.management.views")


@csrf_exempt
def get_nff_ical_events(request):

    request_data = json.loads(request.body)
    url = request_data.get('nffUrl')

    #url = 'http://www.fotball.no/templates/portal/pages/GenerateICalendar.aspx?tournamentid=138918'

    nff_request = requests.get(url)
    event_string_array = nff_request.content.split("BEGIN:VEVENT")
    del event_string_array[0]
    del event_string_array[-1]

    # title_regex = re.compile('DESCRIPTION:.*DTEND:')
    title_regex = re.compile('SUMMARY:.*')
    info_regex = re.compile('DESCRIPTION:.*')
    start_date_regex = re.compile('DTSTART:.*')
    end_date_regex = re.compile('DTEND:.*')
    location_regex = re.compile('LOCATION:.*')
    uid_regex = re.compile('UID:.*')

    team = Team.objects.get(id=request_data.get('teamId'))

    response_data = []
    for event_string in event_string_array:

        #match with regex to extract data:
        event_data = {
            'title': title_regex.search(event_string).group().replace('SUMMARY:', ''),
            'info': info_regex.search(event_string).group().replace('DESCRIPTION:', ''),
            'startDateTime': start_date_regex.search(event_string).group().replace('DTSTART:', ''),
            'endDateTime': end_date_regex.search(event_string).group().replace('DTEND:', ''),
            'location': location_regex.search(event_string).group().replace('LOCATION:', ''),
            'uid': uid_regex.search(event_string).group().replace('UID:', '').strip()
        }

        try:
            event = Event.objects.get(uid=event_data.get('uid'))
            mode = 'update'
        except:
            mode = 'create'
            event = Event()

        event.team = team
        event.title = event_data.get('title')
        event.location = event_data.get('location')
        event.info = event_data.get('info').replace('\\n', '').replace('\\', '')
        event.last_signup_datetime = datetime.datetime.strptime(event_data['startDateTime'].strip(), '%Y%m%d'+'T'+'%H%M%S')
        event.meetup_datetime = datetime.datetime.strptime(event_data['startDateTime'].strip(), '%Y%m%d'+'T'+'%H%M%S')
        event.start_datetime = datetime.datetime.strptime(event_data['startDateTime'].strip(), '%Y%m%d'+'T'+'%H%M%S')
        event.end_datetime = datetime.datetime.strptime(event_data['endDateTime'].strip(), '%Y%m%d'+'T'+'%H%M%S')
        event.uid = event_data.get('uid')
        event.reminder_time = 2
        event.save()

        event_players = []
        if mode == 'create':
            for player in Player.objects.filter(team=team):
                event_player = Event_Player(player=player, event=event, url_hash=generate_url_hash(player.person.username, event.id), sent=False, seen=False, answer=5, comment='').save()
                event_players.append(event_player)

        response_data.append({
                        'mode': mode,
                        'title': event.title,
                        'location': event.location,
                        'info': event.info,
                        'lastSignupDate': event.last_signup_datetime.strftime('%Y%m%d'+'T'+'%H%M%S'),
                        'meetupDateTime': event.meetup_datetime.strftime('%Y%m%d'+'T'+'%H%M%S'),
                        'startDateTime': event.start_datetime.strftime('%Y%m%d'+'T'+'%H%M%S'),
                        'endDateTime': event.end_datetime.strftime('%Y%m%d'+'T'+'%H%M%S'),
                        #'eventGroupId': event.event_group.id,
                        'uid': event.uid,
                        'eventPlayers': event_players
        })

    return HttpResponse(json.dumps(response_data))


def _get_team_data(team):
    return {'id': team.id,'name': team.name, 'players': get_players(team), 'numberOfPlayers': team.players().count() ,'coaches': get_coaches(team)}


def _generate_username(request_data):
    first_name = request_data.get('firstName').encode('utf-8')
    first_name = first_name.lower()
    first_name = first_name.replace(' ','.')
    first_name = first_name.replace('Æ','a')
    first_name = first_name.replace('æ','a')
    first_name = first_name.replace('Ø','o')
    first_name = first_name.replace('ø','o')
    first_name = first_name.replace('Å','a')
    first_name = first_name.replace('å','a')
    first_name = first_name.replace('ü','u')
    first_name = first_name.replace('ö','o')
    first_name = first_name.replace('ä','a')
    first_name = first_name.replace('ë','e')

    last_name = request_data.get('lastName').encode('utf-8')
    last_name = last_name.lower()
    last_name = last_name.replace(' ','.')
    last_name = last_name.replace('Æ','a')
    last_name = last_name.replace('æ','a')
    last_name = last_name.replace('Ø','o')
    last_name = last_name.replace('ø','o')
    last_name = last_name.replace('Å','a')
    last_name = last_name.replace('å','a')
    last_name = last_name.replace('ü','u')
    last_name = last_name.replace('ö','o')
    last_name = last_name.replace('ä','a')
    last_name = last_name.replace('ë','e')

    username = first_name + '.' + last_name + '@sportsfronter.no'
    username = _check_if_unique_username(username)
    logger.debug('generated username: %s' % username)
    return username


def _check_if_unique_username(username):
    if not Person.objects.filter(username=username).exists():
        return username
    else:
        username_array = username.split('@')
        username_array[0] += '_' + str(random.randint(10, 99))
        new_username = username_array[0] + '@' + username_array[1]
        if Person.objects.filter(username=new_username).exists():
            _check_if_unique_username(username)
        else:
            return new_username


def _format_date_of_birth(date):
    if not date:
        return None
    return datetime.datetime.strptime(date, "%Y-%m-%d")


def _get_dateofbirth(person):
    if not person.dateofbirth:
        return ''
    return person.dateofbirth.strftime("%d.%m.%y")
        

def _get_or_create_person(data):
    if not data.get('email'):
        person = _set_person_data(Person(), data)
        return person
    try:
        person = Person.objects.get(username=data.get('email'))
    except:
        person = _set_person_data(Person(), data)
    return person


def _update_or_create_person(data):
    try:
        person = Person.objects.get(username=data.get('email'))
    except:
        person = Person()
    return _set_person_data(person, data)


def _set_person_data(person, data):

    if data.get('email'):
        person.username = data.get('email').lower()
        person.email = data.get('email').lower()
    else:
        person.username = _generate_username(data)
        person.email = ''

    person.first_name = data.get('firstName')
    person.last_name = data.get('lastName')
    person.phone_number = data.get('phoneNumber')
    person.dateofbirth = _format_date_of_birth(data.get('dateOfBirth'))
    person.save()

    return person


def _update_guardians(guardians_data, player):
    if guardians_data:
        new_guardians = [_update_or_create_person(guardian) for guardian in guardians_data]
        for guardian in new_guardians:
            player.guardians.add(guardian)
        for guardian in player.guardians.all():
            if guardian not in new_guardians:
                player.guardians.remove(guardian)
        player.save()

    else:
        for guardian in player.guardians.all():
            player.guardians.remove(guardian)


def _register_events_for_new_player(player, team):
    events = Event.objects.filter(team=team)
    for event in events:
        url_hash = generate_url_hash(player.person.username, event.id)
        Event_Player(player=player, event=event, url_hash=url_hash, sent=False, seen=False, answer=5, comment='').save()

@csrf_exempt
def merge_players(request, team_id):
    if request.method != 'POST' and get_person_from_request(request):
        return HttpResponse("Invalid method or auth", status=400)

    request_data = json.loads(request.body)

    old_username = request_data['oldUserName']
    new_username = request_data['newUserName']

    old_player = Player.objects.get(person__username=old_username)
    new_player = Player.objects.get(person__username=new_username)

    new_player.guardians = old_player.guardians.all()
    new_player.save()

    person = new_player.person
    person.phone_number = old_player.person.phone_number
    person.dateofbirth = old_player.person.dateofbirth
    person.save()

    old_player.delete()

    response_data = {'oldUsername': old_username, 'newUsername': new_username}

    return HttpResponse(json.dumps(response_data),status=200)


@csrf_exempt
@json_response
def save_coach(request, team_id):
    if request.method == 'POST' and get_person_from_request(request):
        data = json.loads(request.body)
        team = Team.objects.get(pk=team_id)
        person = _update_or_create_person(data)
        Team_Coach(person=person, team=team).save()

        team_events = Event.objects.filter(team=team)
        for event in team_events:
            Event_Coach(person=person, event=event, answer=4).save()

        return {'status': 200}
    else:
        return logout_view(request)


@csrf_exempt
@json_response
def remove_coach_from_team(request, team_id):
    if not (request.method == 'POST' and get_person_from_request(request)):
        return logout_view(request)
    data = json.loads(request.body)
    team = Team.objects.get(pk=team_id)
    person = _get_or_create_person(data)
    person.coach_roles.remove(team)
    return {'status': 200}


def _check_username(guardians, player_email):
    for guardian in guardians:
        if guardian.get('email') == player_email:
            return 'Spiller og foresatte må ha forskjellig e-mail.'
    return None


@csrf_exempt
@json_response
def guardian_connect_to_player(request, team_id):

    if request.method != 'POST' or not get_person_from_request(request):
        return json_error("wrong method or auth")

    user_person = get_person_from_request(request)
    if not user_person:
        return HttpResponse("Not logged in.", status=400)

    request_data = json.loads(request.body)
    player_username = request_data.get('playerUserName')

    team = Team.objects.get(pk=team_id)
    player = Player.objects.get(person__username=player_username,team=team)
    person = player.person

    if request_data.get('playerPhoneNumber', None):
        person.phone_number = request_data.get('playerPhoneNumber')
        person.save()

    if request_data.get('playerBirthDate', None):
        dateofbirth = _format_date_of_birth(request_data.get('playerBirthDate'))
        person.dateofbirth = dateofbirth
        person.save()

    player.guardians.add(user_person)
    player.save()

    response_data = {'player': player.person.username, 'guardian': user_person.username}
    return HttpResponse(json.dumps(response_data), status=200)


@csrf_exempt
@json_response
def guardian_add_player(request, team_id):
    if request.method != 'POST' or not get_person_from_request(request):
        return json_error("wrong method or auth")

    user_person = get_person_from_request(request)
    if not user_person:
        return HttpResponse("Not logged in.", status=400)

    request_data = json.loads(request.body)

    team = Team.objects.get(pk=team_id)

    if not request_data.get('playerIsChecked'):
        #if registering player as a new guardian: check if player with that name already exists
        teamPlayers = Player.objects.filter(team=team)
        existingPlayers = teamPlayers.filter(person__first_name=request_data.get('firstName'), person__last_name=request_data.get('lastName'))

        if existingPlayers:
            existingPlayersArray = []
            for existingPlayer in existingPlayers:
                existingPlayersArray.append(player_detail(existingPlayer.id))
            response_data = {'existingPlayers': existingPlayersArray}
            return HttpResponse(json.dumps(response_data), status=200)

    person = _get_or_create_person(request_data)

    player = Player()
    player.person = person
    player.team = team
    player.shirt_number = request_data.get('shirtNumber', None)
    player.activated = False
    player.save()

    response_data = {'status': 'player added'}

    _register_events_for_new_player(player, team)

    #if adding player when registering as a guardian, register yourself as a guardian:
    if request_data.get('newGuardian'):
        player.guardians.add(user_person)
        player.save()
        response_data['guardian_added'] = True
    else:
        #update guardians the normal way
        _update_guardians(request_data.get('guardians'), player)

    return HttpResponse(json.dumps(response_data), status=200)


@csrf_exempt
def join_team(request, team_id):
    if request.method != 'POST' or not get_person_from_request(request):
        return json_error("wrong method or auth")

    person = get_person_from_request(request)
    if not person:
        return HttpResponse("Not logged in.", status=400)

    request_data = json.loads(request.body)

    team = Team.objects.get(pk=team_id)

    response_data = {'player': False, 'guardian': False, 'manager': False}

    if request_data.get('player'):
        existingPlayers = Player.objects.filter(person__username=person.username, team=team)
        if existingPlayers:
            response_data['existingPlayers'] = [{'userName': existingPlayer.person.username} for existingPlayer in existingPlayers]
            response_data['errorMessage'] = "Du er allerede spiller på laget."
            return HttpResponse(json.dumps(response_data), status=400)
        player = Player()
        player.person = person
        player.team = team
        player.activated = True
        player.save()
        response_data['player'] = True

    ##guardians join by using the guardian_add_player-function

    if request_data.get('manager'):
        existingCoachRoles = person.coach_roles.all()
        if team in existingCoachRoles:
            response_data['errorMessage'] = "Du er allerede lagleder på dette laget."
            return HttpResponse(json.dumps(response_data), status=400)

        Team_Coach(person=person, team=team).save()
        response_data['guardian'] = True

    return HttpResponse(json.dumps(response_data), status=200)


@csrf_exempt
@json_response
def add_player(request, team_id):
    if request.method != 'POST' or not get_person_from_request(request):
        return json_error("wrong method or auth")

    user_person = get_person_from_request(request)
    if not user_person:
        return HttpResponse("Not logged in.", status=400)

    request_data = json.loads(request.body)

    person = _get_or_create_person(request_data)
    team = Team.objects.get(pk=team_id)

    player = Player()
    player.person = person
    player.team = team
    player.shirt_number = request_data.get('shirtNumber', None)
    player.activated = False
    player.save()

    response_data = {'status': 'player added'}

    _register_events_for_new_player(player, team)
    _update_guardians(request_data.get('guardians'), player)

    return HttpResponse(json.dumps(response_data), status=200)


@csrf_exempt
@json_response
def update_player(request, player_id):
    if not (request.method == 'POST' and get_person_from_request(request)):
        return json_error("wrong method or auth")

    user_person = get_person_from_request(request)
    if not user_person:
        return HttpResponse("Not logged in.", status=400)

    data = json.loads(request.body)

    player = Player.objects.get(pk=player_id)
    player.person.first_name = data.get('firstName')
    player.person.last_name = data.get('lastName')
    player.person.dateofbirth = _format_date_of_birth(data.get('dateOfBirth'))
    player.person.email = data.get('email')
    player.person.phone_number = data.get('phoneNumber')
    player.shirt_number = data.get('shirtNumber')
    player.team = Team.objects.get(id=data.get('teamId'))
    player.save()
    player.person.save()
    _update_guardians(data.get('guardians'), player)
    return {'status': 200}


def return_date(player_id):
    player = Player.objects.get(pk=player_id)
    tempDateBirth = player.person.dateofbirth
    if tempDateBirth:
        dateBirth = tempDateBirth.strftime('%Y-%m-%d')
        return dateBirth
    return ""


def is_player_and_coach(player):
    if player.team in player.person.coach_roles.all():
        return True
    else:
        return False


def player_detail(player_id):
    player = Player.objects.get(pk=player_id)
    dateBirth = return_date(player_id)
    player_info = {
    'username': player.person.username,
    'id': player.id,
    'isCoach': is_player_and_coach(player),
    'phoneNumber': player.person.phone_number,
    'email': player.person.email,
    'firstName': player.person.first_name,
    'lastName': player.person.last_name,
    'dateOfBirth': dateBirth,
    'shirtNumber': player.shirt_number,
    'guardians': [{
                  'firstName': guardian.first_name,
                  'lastName': guardian.last_name,
                  'email': guardian.email,
                  'phoneNumber': guardian.phone_number,
                  'id': guardian.id
                  } for guardian in player.guardians.all()],
    }
    return player_info


@csrf_exempt
def get_player_info(request, player_id):
    if request.method != 'GET':
        return HttpResponse("fail", content_type="application/json")

    person = get_person_from_request(request)

    if not person:
        return logout_view(request)

    json_data = json.dumps(player_detail(player_id))
    return HttpResponse(json_data, content_type="application/json")
        


def is_player_for_team(team, person):
    if Player.objects.filter(person=person, team=team, is_active=True).exists():
        return True
    else:
        return False


@json_response
@csrf_exempt
def get_coach_info(request, team_id, coach_id):
    if not (request.method == 'GET' and get_person_from_request(request)):
        return logout_view(request)

    coach = Person.objects.get(pk=coach_id)
    return {
    'id': coach.id,
    'phoneNumber': coach.phone_number,
    'email': coach.email,
    'firstName': coach.first_name,
    'lastName': coach.last_name,
    'isPlayer': is_player_for_team(Team.objects.get(pk=team_id), coach)
    }


@csrf_exempt
@json_response
def add_player_as_coach(request, team_id, player_id):
    if not (request.method == 'GET' and get_person_from_request(request)):
        return logout_view(request)

    person = Player.objects.get(pk=player_id).person
    team = Team.objects.get(pk=team_id)
    Team_Coach(person=person, team=team).save()
    return {'status': 200}


@csrf_exempt
@json_response
def remove_from_team(request, player_id):
    if request.method != 'GET':
        return {'error': 'fail in remove from team'}

    person = get_person_from_request(request)
    if person:
        player = Player.objects.get(pk=player_id)
        player.is_active = False
        player_data = {
            'username': player.person.username,
            'id': player_id,
        }
        player.delete()
        return {'removed': player_data}


@csrf_exempt
@json_response
def add_team(request):
    if request.method != 'POST':
        return json_error('Method should be POST')
    person = get_person_from_request(request)
    if not person:
        return logout_view(request)
    data = json.loads(request.body)
    team = Team(name=data.get('teamname'))
    team.save()
    Team_Coach(person=person, team=team).save()
    return {'team_id': team.id}
        


def get_players(team, sortkey='lastName'):
    players = Player.objects.filter(team=team, is_active=True)
    players_list = [{
                    'username': player.person.username,
                    'id': player.id,
                    'firstName': player.person.first_name,
                    'lastName': player.person.last_name,
                    'email': player.person.email,
                    'shirtNumber': player.shirt_number,
                    'guardians': [
                        {'name': guardian.first_name + ' ' + guardian.last_name, 'email': guardian.email, 'phoneNumber': guardian.phone_number}
                        for guardian in player.guardians.all()],
                    'phoneNumber': player.person.phone_number,
                    'dateOfBirth': _get_dateofbirth(player.person),
                    'teamId': team.id
                    } for player in players]
    return sorted(players_list, key=lambda k: k[sortkey])


def get_coaches(team, sortkey='lastName'):
    coaches = Person.objects.filter(coach_roles=team)
    coaches_list = [{'id': coach.id, 'firstName': coach.first_name, 'lastName': coach.last_name,
                     'phoneNumber': coach.phone_number} for coach in coaches]
    return sorted(coaches_list, key=lambda k: k[sortkey])


@csrf_exempt
@json_response
def get_team(request, team_id):
    if request.method != 'GET':
        return HttpResponse("Bad Request", status=400)
    team = Team.objects.get(pk=team_id)
    return _get_team_data(team)


@csrf_exempt
@json_response
def team_search(request, search_term):
    if request.method != 'GET':
        return HttpResponse("Bad Request", status=400)


    teams = Team.objects.filter(name__icontains=search_term)

    response_data = {'results': []}
    if teams:
        response_data['results'] = [{'id': team.id, 'name': team.name, 'players': get_players(team), 'numberOfPlayers': team.players().count(), 'coaches': get_coaches(team)} for team in teams]

    return response_data


@csrf_exempt
def get_team_name(request, team_id):
    if request.method != 'GET':
        return json_error("Method is POST")

    person = get_person_from_request(request)

    if not person:
        return logout_view(request)

    response_data = {}
    team = Team.objects.get(pk=team_id)

    if team in person.coach_roles.all():
        status = 200
        response_data = {
        'team_name': team.name
        }
    else:
        response_data = {}
        status = 400

    json_data = json.dumps(response_data)

    return HttpResponse(json_data, content_type="application/json", status=status)


@csrf_exempt
def get_teams(request):
    if request.method != 'GET':
        return json_error('not get in xmlHttpRequest')

    person = get_person_from_request(request)
    if not person:
        return logout_view(request)

    teams = person.coach_roles.all()
    teams_dict = [{'id': team.id, 'name': team.name,
                   'number_of_players': Player.objects.filter(team=team).filter(is_active=True).count()} for
                  team in teams]
    json_data = json.dumps(teams_dict)
    return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def get_all_teams(request):
    if request.method != 'GET':
        return json_error('not get in xmlHttpRequest')

    person = get_person_from_request(request)
    if not person:
        return logout_view(request)

    coach_teams = person.coach_roles.all()
    coach_teams_dict = [{'id': coach_team.id, 'name': coach_team.name,
                   'numberOfPlayers': Player.objects.filter(team=coach_team).filter(is_active=True).count()} for
                  coach_team in coach_teams]


    guardian_roles = person.guardian.all()
    guardian_teams = []
    for guardian_role in guardian_roles:
        team = guardian_role.team
        if not team in guardian_teams:
            guardian_teams.append(team)
    guardian_teams_dict = [{'id': guardian_team.id, 'name': guardian_team.name} for guardian_team in guardian_teams]

    player_roles = Player.objects.filter(person=person)
    player_teams_dict = [{'id': player_role.team.id, 'name': player_role.team.name} for player_role in player_roles]

    response_data = {'coachTeams': coach_teams_dict, 'guardianTeams': guardian_teams_dict, 'playerTeams': player_teams_dict}

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def delete_team(request):
    if request.method != 'POST':
        return HttpResponse('not POST in xmlHttpRequest', status=400)

    person = get_person_from_request(request)
    if not person:
        return HttpResponse("Error: not logged in", status=400)

    request_data = json.loads(request.body)
    team_id = request_data['team_id']
    team_name = request_data['team_name']

    team = person.coach_roles.get(name=team_name)
    team.delete()

    response_data = {'team_id': team_id, 'team_name': team.name}

    return HttpResponse(json.dumps(response_data), status=200)


@csrf_exempt
def change_team_name(request):
    if request.method != 'POST':
        return HttpResponse('not POST in xmlHttpRequest', status=400)

    person = get_person_from_request(request)
    if not person:
        return HttpResponse("Error: not logged in", status=400)

    request_data = json.loads(request.body)
    team_id = request_data['team_id']
    old_team_name = request_data['old_team_name']
    new_team_name = request_data['new_team_name']

    team = person.coach_roles.get(name=old_team_name)
    team.name = new_team_name
    team.save()

    response_data = {'team_id': team_id, 'old_team_name': old_team_name, 'new_team_name': new_team_name}

    return HttpResponse(json.dumps(response_data), status=200)


@csrf_exempt
def get_person_from_email(request, player_email):
    if request.method != 'GET':
        return HttpResponse('method must be GET', status=400)
    user_person = get_person_from_request(request)
    if not user_person:
        return HttpResponse("Error: not logged in", status=400)

    try:
        person = Person.objects.get(username=player_email)
    except:
        response_data = {'person_exists': False}
        return HttpResponse(json.dumps(response_data), status=200)

    teams = []
    for player in person.player_set.all():
        teams.append({'team_id': player.team.id, 'team_name': player.team.name})

    coach_roles = []
    for coach_role in person.coach_roles.all():
        coach_roles.append(coach_role.pk)

    if person.dateofbirth:
        dateofbirth = person.dateofbirth.strftime("%Y-%m-%d")
    else:
        dateofbirth = None

    response_data = {'person_exists': True,
                     'username': person.username,
                     'first_name': person.first_name,
                     'last_name': person.last_name,
                     'birthdate': dateofbirth,
                     'phone_number': person.phone_number,
                     'activated': person.activated,
                     'teams': teams,
                     'coach_roles': coach_roles,
                                                            }

    return HttpResponse(json.dumps(response_data), status=200)


@csrf_exempt
def get_user_info(request):
    if request.method != 'GET':
        return json('not a GET request')

    person = get_person_from_request(request) 
    if not person:
        return logout_view(request)

    if person.dateofbirth:
        dateofbirth = person.dateofbirth.strftime("%Y-%m-%d")
    else:
        dateofbirth = None

    response_data = {
                     'username':person.username,
                     'first_name':person.first_name,
                     'last_name':person.last_name,
                     'phone_number':person.phone_number,
                     'dateofbirth': dateofbirth,
                     }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def update_user_info(request):
    if request.method != 'POST':
        return HttpResponse("Method must be POST", status=400)

    person = get_person_from_request(request) 
    if not person:
        return logout_view(request)

    request_data = json.loads(request.body)

    if request_data.get('dateOfBirth'):
        dateofbirth = _format_date_of_birth(request_data.get('dateOfBirth'))
    else:
        dateofbirth = None

    old_username = person.username
    new_username = request_data.get('userName')

    if (Person.objects.filter(username=new_username) and new_username != old_username):
        response_data = {'error': 'username taken'}
        return HttpResponse(json.dumps(response_data), status=400)

    person.username = request_data.get('userName')

    person.email = request_data.get('userName')
    person.first_name = request_data.get('firstName')
    person.last_name = request_data.get('lastName')
    person.phone_number = request_data.get('phoneNumber')
    person.dateofbirth = dateofbirth
    person.save()

    if person.dateofbirth:
        dateofbirth = person.dateofbirth.strftime("%Y-%m-%d")
    else:
        dateofbirth = None

    new_username = person.username

    if old_username != new_username:
        send_username_update_mail(person, old_username, new_username)

    response_data = {'username': person.username,
                     'first_name': person.first_name,
                     'last_name': person.last_name,
                     'phone_number': person.phone_number,
                     'dateofbirth': dateofbirth,
                     }

    return HttpResponse(json.dumps(response_data), status=200)


def get_guardian_players_for_team(request, team_id):

    if request.method != 'GET':
        return HttpResponse("Method must be GET", status=400)

    person = get_person_from_request(request) 
    if not person:
        return logout_view(request)

    team = Team.objects.get(pk=team_id)

    players = Player.objects.filter(team=team)

    children = []

    for player in players:
        if not player.guardians:
            continue
        for guardian in player.guardians.all():
            if person.username == guardian.username:
                child_info = {
                    'firstName': player.person.first_name,
                    'lastName': player.person.last_name,
                    'dateOfBirth': _get_dateofbirth(player.person),
                    'shirtNumber': player.shirt_number
                }

                children.append(child_info)

    response_data = {'children': children}
    
    return HttpResponse(json.dumps(response_data), status=200)




