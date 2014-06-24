#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from event.models import Person, Device, Player, Team, Team_Coach

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

import requests
import time
import json
import datetime
import logging

logger = logging.getLogger("sportsfronter.auth.views")


def _get_user_roles(person):
    user_roles = {
        'player': [],
        'guardian': [],
        'coach': []
    }

    player_roles = Player.objects.filter(person=person)
    if player_roles:
        for player_role in player_roles:
            user_roles['player'].append(player_role.team.id)

    guardian_roles = person.guardian
    if guardian_roles:
        for guardian_role in guardian_roles.all():
            user_roles['guardian'].append({'username': guardian_role.person.username, 'teamId': guardian_role.team.id})

    coach_roles = person.coach_roles.all()
    if coach_roles:
        for coach_role in coach_roles:
            user_roles['coach'].append(coach_role.id)

    return user_roles

def get_user_roles(request):

    person = get_person_from_request(request)

    if not person or request.method != 'GET':
        return HttpResponse('Invalid request or auth', status=400)

    user_roles = {
        'player': [],
        'guardian': [],
        'coach': []
    }

    player_roles = Player.objects.filter(person=person)
    if player_roles:
        for player_role in player_roles:
            user_roles['player'].append(player_role.team.id)

    guardian_roles = person.guardian
    if guardian_roles:
        for guardian_role in guardian_roles.all():
            user_roles['guardian'].append({'username': guardian_role.person.username, 'teamId': guardian_role.team.id})

    coach_roles = person.coach_roles.all()
    if coach_roles:
        for coach_role in coach_roles:
            user_roles['coach'].append(coach_role.id)

    return HttpResponse(json.dumps(user_roles), status=200)


#used when someone registers with invite link:
def _create_player(person, team_id):

    #check if person is already a player on this team:
    existingPlayer = Player.objects.filter(person=person, team__id=team_id)
    if existingPlayer:
        return False

    player = Player()
    player.person = person
    team = Team.objects.get(pk=team_id)
    player.team = team
    player.save()
    return True


def _create_manager(person, team_id):
    team = Team.objects.get(id=team_id)
    Team_Coach(person=person, team=team).save()
    return True


def username_is_present(username):
    if User.objects.filter(username=username).count():
        return True
    else:
        return False


def user_is_activated(username):
    person = Person.objects.get(username=username)
    return person.activated


def set_cookie(response, key, value, domain, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=domain, secure=False, httponly=False)


def get_person_from_request(request):
    """
    supports both token and session auth

    """
    if request.user.is_authenticated():
        try:
            return request.user.person
        except:
            return False
    token = request.META.get('HTTP_AUTHORIZATION')
    if token:
        try:
            return Token.objects.get(pk=token).user.person
        except:
            return False
    else:
        return False


@csrf_exempt
def is_auth(request):
    if request.user.is_authenticated():
        return HttpResponse(json.dumps({'is_auth': True, 'name': request.user.first_name+ " " +request.user.last_name}),
                            content_type="application/json")
    else:
        logout(request)
        return HttpResponse(json.dumps({'is_auth': False}), content_type="application/json")


def add_android_device(user, gcm_regid):
    try:
        """
        Adds device to user.person, only if the same device is not present.
        """
        if Device.objects.filter(registration_id=gcm_regid).count() < 1:
            Device(owner=user.person, registration_id=gcm_regid, device_type="android").save()
        else:
            device = Device.objects.get(registration_id=gcm_regid)
            device.owner = user.person
            device.save()
        return True
    except:
        return False

def add_ios_device(user, ios_token):
    try:
        """
        Adds device to user.person, only if the same device is not present.
        """
        if Device.objects.filter(registration_id=ios_token).count() < 1:
            Device(owner=user.person, registration_id=ios_token, device_type="ios").save()
        else:
            device = Device.objects.get(registration_id=ios_token)
            device.owner = user.person
            device.save()
        return True
    except:
        return False


@csrf_exempt
def _login(request):
    data = json.loads(request.body)

    users = Person.objects.filter(username=data['username'])
    if not users:
        return HttpResponse("Feil: Brukeren er ikke opprettet. Registrer deg først!", status=400)
    for user in users:
        if not user.password:
            return HttpResponse("Feil: Brukeren er ikke opprettet. Registrer deg først!", status=400)

    user = authenticate(username=data['username'], password=data['password'])
    logger.info("data: " + json.dumps(data))
    if user is not None:
        if user.is_active:
            if 'gcm_regid' in data and len(data['gcm_regid']) > 20:
                add_android_device(user, data['gcm_regid'])
            if 'ios_token' in data:
                add_ios_device(user, data['ios_token'])
                logger.info("ios token info: " + data['ios_token'])
            login(request, user)
            has_team = user.person.coach_roles.count() > 0

            try:
                token = Token.objects.get(user=user).pk
            except:
                token = Token.objects.create(user=user).pk

            response_data = {'login': True,
                             'firstName': user.first_name,
                             'lastName': user.last_name,
                             'auth_token': token,
                             'has_team': has_team
                             }

            #if registering via invite link, add user to team:
            username = data['username']
            team_id = data.get('teamId', None)
            user_roles = data.get('userRoles', None)
            person = Person.objects.get(username=username)

            if team_id:
                if user_roles.get('player'):
                    _create_player(person, team_id)

            response_data['userRoles'] = _get_user_roles(person)

            logger.info("User %s logged in." % data['username'])

            return HttpResponse(json.dumps(response_data), status=200)
        else:
            # Return a 'disabled account' error message
            logger.info("User %s failed to log in (disabled account)." % data['username'])
            return HttpResponse(json.dumps({'login': 'not active'}), content_type="application/json")
    else:
        # Return an 'invalid login' error message.
        logger.info("User %s failed to log in (invalid username or password)." % data['username'])
        return HttpResponse(json.dumps({'login': False}), content_type="application/json")


@csrf_exempt
def register(request):

    data = json.loads(request.body)

    username = data['username'].lower()
    first_name = data['firstName']
    last_name = data['lastName']
    team_id = data.get('teamId', None)
    user_roles = data.get('userRoles', None)

    logger.info("data: " + json.dumps(data))

    if username_is_present(username):
        # If a user has not logged in and activated account we activate it and sets its password
        if not user_is_activated(username):
            person = Person.objects.get(username=username)
            person.set_password(data['password'])
            person.activated = True
            person.save()

            if Token.objects.filter(user=person).count() == 0:
                Token.objects.create(user=person).save()

            #send user info to isave API:
            response_data = send_user_info(person)
            response_data['register'] = True

            #add person to team (if person used an invite link)
            response_data['roles'] = []
            if team_id:
                if user_roles.get('player'):
                    if user_roles['player']:
                        _create_player(person, team_id)
                        response_data['roles'].append('player')

                if user_roles.get('guardian'):
                    response_data['roles'].append('guardian')

                if user_roles.get('manager'):
                    if user_roles['manager']:
                        _create_manager(person, team_id)
                        response_data['roles'].append('manager')

                response_data['teamId'] = team_id

            #return HttpResponse(json.dumps({'register': True}), content_type="application/json")
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'register': False}), content_type="application/json")
    else:
        person = Person(username=username, email=username, first_name=first_name, last_name=last_name)
        person.set_password(data['password'])
        person.activated = True
        person.save()
        Token.objects.create(user=person).save()

        #add person to team

        #send user info to isave API:
        response_data = send_user_info(person)

        #add person to team (if person used an invite link)
        response_data['roles'] = []
        if team_id:
            if user_roles.get('player'):
                if user_roles['player']:
                    _create_player(person, team_id)
                    response_data['roles'].append('player')

            if user_roles.get('guardian'):
                response_data['roles'].append('guardian')

            if user_roles.get('manager'):
                if user_roles['manager']:
                    _create_manager(person, team_id)
                    response_data['roles'].append('manager')

            response_data['teamId'] = team_id
        
        response_data['register'] = True

        return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def logout_view(request):
    logout(request)
    return HttpResponse(json.dumps({'logout': True}), content_type="application/json")


@csrf_exempt
def send_user_info(person):

    url = "http://dialog.isave.no/mrm/services/api.asmx?op=InsertDatalistContact"
    headers = {'content-type': 'text/xml; charset=utf-8'}

    payload = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <InsertDatalistContact xmlns="http://isave.no/">
      <username>SFAPIuser</username>
      <password>04E332ECAAB7CCF283957F5483E71700</password>
      <contact>
        <ContactID>1202</ContactID>
        <Email>""" + str(person.email) + """</Email>
        <DemograficData></DemograficData>
        <Stamp>""" + time.strftime("%H:%M:%S") + """</Stamp>
        <Mobile>""" + str(person.phone_number) + """</Mobile>
        <FirstName>""" + u''.join(person.first_name).encode('utf-8') + """</FirstName>
        <LastName>""" + u''.join(person.last_name).encode('utf-8') + """</LastName>
        <CompanyReference />
      </contact>
      <datalistID>569834</datalistID>
    </InsertDatalistContact>
  </soap:Body>
</soap:Envelope>"""

    r = requests.post(url, data=payload, headers=headers)
    response_data = {'isave_status code': r.status_code, 'save_reason': r.reason, 'isave_content': r.content}

    return response_data


