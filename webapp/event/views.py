 #!/usr/bin/python
 #coding: utf8

import json
import datetime
import hashlib
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from event.models import Player, Event, Event_Player, Team, Person, Event_Group, Team_Coach, Event_Coach
from push.views import push_out_new_events
from auth.views import get_person_from_request, logout_view
from event.email_utils import send_update_mail, send_invite_mail, send_event_group_invite_and_update_mail

logger = logging.getLogger("sportsfronter.event.views")


def _rsvp_coach_and_player(person, event, answer):
    user_event_coach = Event_Coach.objects.get(person=person, event=event)
    user_event_coach.answer = answer
    user_event_coach.save()
    #rsvp for case where coach is also a player/attendee:
    try:
        player = Player.objects.get(person=person, team=event.team)
        event_player = Event_Player.objects.get(player=player, event=event)
        event_player.answer = answer
        event_player.seen = True
        event_player.save()
        event_player_updated = True
    except:
        event_player_updated = False
    return event_player_updated


def _update_event_coaches(event):
    existing_event_coaches = Event_Coach.objects.filter(event=event)
    if not existing_event_coaches:
        team_coaches = Team_Coach.objects.filter(team=event.team)
        for team_coach in team_coaches:
            Event_Coach(person=team_coach.person, event=event, answer=4).save()
    return True


def _update_event_players(attendees, event, notInvitedList, shareEvent):
    #delete event_players that have been removed from event:
    existing_event_players = Event_Player.objects.filter(event=event)
    for existing_event_player in existing_event_players:
        if existing_event_player.player.person.username in notInvitedList:
            existing_event_player.delete()
            #TODO send notification about being removed from event

    #add new attendees:
    for attendee in attendees:
        person = Person.objects.get(username=attendee['username'])
        url_hash = generate_url_hash(person.username, event.id)
        team = Team.objects.get(id=attendee['teamId'])
        player = Player.objects.get(person=person, team=team)

        if person.username in notInvitedList:
            continue
        if Event_Player.objects.filter(event=event, player=player):
            continue
        if shareEvent:
            Event_Player(player=player, event=event, url_hash=url_hash, sent=True, seen=False, answer=4, comment='').save()
            continue
        Event_Player(player=player, event=event, url_hash=url_hash, sent=False, seen=False, answer=5, comment='').save()

    return True


def _send_invites_and_updates(event):
    already_invited_event_players = []
    new_event_players = []

    event_players = Event_Player.objects.filter(event=event)

    for event_player in event_players:
        if event_player.sent:
            push_out_new_events(event_player.player, event, "update", event_player.url_hash)
            already_invited_event_players.append(event_player)
        else:
            push_out_new_events(event_player.player, event, "invite", event_player.url_hash)
            new_event_players.append(event_player)

    send_update_mail(already_invited_event_players, event)
    send_invite_mail(new_event_players, event)
    return True


def _send_invites_and_updates_event_group(event_group):
    events = event_group.events.all()
    existing_event_players = []
    new_event_players = []
    for event in events:

        event_players = Event_Player.objects.filter(event=event)

        for event_player in event_players:
            if event_player.sent:
                push_out_new_events(event_player.player, event, "update", event_player.url_hash)
                existing_event_players.append(event_player)
            else:
                push_out_new_events(event_player.player, event, "invite", event_player.url_hash)
                new_event_players.append(event_player)

    send_event_group_invite_and_update_mail(new_event_players, existing_event_players)

    return True


def json_error(msg):
    return HttpResponse(json.dumps({'error': msg}),  content_type="application/json")


def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json.
    """
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = json.dumps(objects)
        except:
            data = json.dumps(str(objects))
        return HttpResponse(data, "application/json")
    return decorator


def generate_url_hash(username, event_id):
    salt = "hashing_is_cool"
    temp_hash = username + str(event_id)
    temp_hash = temp_hash.encode('ascii', 'ignore')
    url_hash = hashlib.sha1(temp_hash)
    url_hash.update(salt)
    return url_hash.hexdigest()


@csrf_exempt
def return_events_coach(request):
    if request.method != 'GET':
        return HttpResponse(json.dumps({'status': 'fail'}), content_type="application/json")

    person = get_person_from_request(request)
    if not person:
        return logout_view(request)

    teams = person.coach_roles.all()
    events = []
    now = datetime.datetime.now()

    for team in teams:
        team_events = Event.objects.filter(team=team)
        for team_event in team_events:
            event_datetime = team_event.meetup_datetime.replace(tzinfo=None)
            delta = now - event_datetime
            if delta.days < 7 and now < event_datetime:
                events.append(team_event)

    events_dict = return_events_list(events)
    json_data = json.dumps(events_dict)
    return HttpResponse(json_data, content_type="application/json")


def build_json_event(event):
    start_datetime = datetimeformat(event.start_datetime)
    meetup_datetime = datetimeformat(event.meetup_datetime)
    end_datetime = datetimeformat(event.end_datetime)
    last_signup_datetime = datetimeformat(event.last_signup_datetime)

    data = {
            'id': event.id, 
            'title': event.title,
            'date': start_datetime['date'],
            'startTime': start_datetime['time'],
            'meetupTime': meetup_datetime['time'],
            'endTime': end_datetime['time'],
            'lastSignupDate': last_signup_datetime['date'],
            'lastSignupTime': last_signup_datetime['time'],
            'location': event.location,
            'info': event.info,
            'team': {'id': event.team.id, 'name': event.team.name},
            'opponent': event.opponent,
            'reminderTime': event.reminder_time,
            }

    if event.event_group:
        data['eventGroup'] = {'id': event.event_group.id, 'title': event.event_group.title}

    return data


@json_response
@csrf_exempt
def get_event(request, event_id):
    if request.method != 'GET':
        return json_error("wrong METHOD")

    person = get_person_from_request(request)
    if not person:
        return logout_view(request)

    event = Event.objects.get(pk=event_id)
    attendees =  Event_Player.objects.filter(event=event)

    team_players = []
    for team_player in event.team.team_player.all():
        team_player_object = {
                              'username': team_player.person.username,
                              'email': team_player.person.email,
                              'firstName': team_player.person.first_name,
                              'lastName': team_player.person.last_name,
                              'teamId': event.team.id,
                              }
        team_players.append(team_player_object)

    coaches = []
    for event_coach in Event_Coach.objects.filter(event=event):
        event_coach_dict = {
            'username': event_coach.person.username,
            'firstName': event_coach.person.first_name,
            'lastName': event_coach.person.last_name,
            'answerInt': event_coach.answer
        }
        coaches.append(event_coach_dict)

    try:
        user_event_coach = Event_Coach.objects.get(event=event, person=person)
        user_answer = user_event_coach.answer
    except:
        user_answer = None

    response_data = {'event': build_json_event(event),
                     'attendees': get_attendees_sorted(attendees),
                     'teamPlayers': team_players,
                     'coaches': coaches,
                     'userAnswerInt': user_answer}

    return HttpResponse(json.dumps(response_data), status=200)


def save_event_info(request_data, event=None, date=None, event_group=None):
    team = Team.objects.get(pk=request_data['team'])
    if not event:
        try:
            event = Event.objects.get(pk=request_data['eventId'])
        except:
            event = Event()

    event.title = request_data['title']
    event.team = team
    event.location = request_data['location']   
    event.info = request_data['info'] or ""
    event.opponent = request_data['opponent'] or ""

    if date:
        date_string = date.strftime('%Y-%m-%d')
    else:
        date_string = request_data['date']

    event.meetup_datetime = datetime.datetime.strptime(date_string + " " + request_data['meetupTime'], '%Y-%m-%d %H:%M')
    event.start_datetime = datetime.datetime.strptime(date_string + " " + request_data['startTime'], '%Y-%m-%d %H:%M')
    event.end_datetime = datetime.datetime.strptime(date_string + " " + request_data['endTime'], '%Y-%m-%d %H:%M')

    event.reminder_time = request_data['reminderTime']

    if request_data.get('lastSignupDate') and request_data.get('lastSignupTime'):
        event.last_signup_datetime = datetime.datetime.strptime(request_data['lastSignupDate'] + " " + request_data['lastSignupTime'], '%Y-%m-%d %H:%M')
    else:
        event.last_signup_datetime = None

    if event_group:
        event.event_group = event_group
        event_group.save()

    event.save()
    _update_event_players(request_data['attendees'], event, request_data['notInvited'], request_data['shareEvent'])
    _update_event_coaches(event)

    return event


def save_event_group(request_data, update_all_events, user):

    #update event group:
    if update_all_events:
        event_group = Event_Group.objects.get(pk=request_data.get('eventGroupId'))

        for event in event_group.events.all():
            save_event_info(request_data, event=event, date=event.meetup_datetime, event_group=event_group)
            _rsvp_coach_and_player(user, event, 1)

        if not request_data['sendNotification']:
            response_data = {'eventGroupId': event_group.id, 'update': False}
            return response_data
            
        _send_invites_and_updates_event_group(event_group)
        response_data = {'eventGroupId': event_group.id, 'update': True}
        return response_data

    #create event group:
    if request_data.get('eventGroupTitle'):
        event_group = Event_Group(title=request_data['eventGroupTitle'])
    else:
        event_group = Event_Group(title=request_data['title'])

    event_group.save()

    event_period_start_datetime = datetime.datetime.strptime(request_data['recurringEventStartDate'] + " " + request_data['meetupTime'], '%Y-%m-%d %H:%M')
    event_period_end_datetime = datetime.datetime.strptime(request_data['recurringEventEndDate'] + " " + request_data['meetupTime'], '%Y-%m-%d %H:%M')

    recurring_event_frequency = int(request_data.get('recurringEventFrequency'))

    if recurring_event_frequency == 1:
        timedelta = datetime.timedelta(days=7)
    elif recurring_event_frequency == 2:
        timedelta = datetime.timedelta(days=30)

    #create events:
    temp_date = event_period_start_datetime
    event_list = []
    while temp_date <= event_period_end_datetime:
        event = save_event_info(request_data, date=temp_date, event_group=event_group)
        _rsvp_coach_and_player(user, event, 1)

        event_list.append(event.id)
        temp_date += timedelta

    #send emails and push messages:
    if not request_data['sendNotification']:
        response_data = {'eventGroupId':event_group.id, 'events': event_list,'sendNotification': False}
        return response_data

    _send_invites_and_updates_event_group(event_group)
    response_data = {'eventGroupId':event_group.id, 'events': event_list,'send_notification': True}
    return response_data


@csrf_exempt
def save_event(request):
    if request.method != 'POST':
        return json_error("Method should be POST")

    request_data = json.loads(request.body)

    user = get_person_from_request(request)

    if request_data.get('recurringEvent') and not request_data.get('eventGroupId'):
        #create new event group
        response_data = save_event_group(request_data, False, user)
        return HttpResponse(json.dumps(response_data), status=200)

    if request_data.get('eventGroupId') and request_data.get('editAllEventsInGroup'):
        #update event group
        response_data = save_event_group(request_data, True, user)
        return HttpResponse(json.dumps(response_data))

    event = save_event_info(request_data)

    #assuming that event creator is attending:
    event_player_status = _rsvp_coach_and_player(user, event, 1)

    #send emails and push messages:
    if not request_data['sendNotification']:
        response_data = json.dumps({'event_id':event.id, 'sendNotification': False, 'eventPlayerStatus': event_player_status})
        return HttpResponse(response_data,  content_type="application/json")

    _send_invites_and_updates(event)

    response_data = json.dumps({'event_id':event.id, 'send_notification': True, 'eventPlayerStatus': event_player_status})
    return HttpResponse(response_data,  content_type="application/json")


@csrf_exempt
def delete_event(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'error': 'in delete_event in views'}))

    request_data = json.loads(request.body)

    if 'event_id' not in request_data:
        return HttpResponse(json.dumps({'status':400}),  content_type="application/json")

    if request_data.get('eventGroupId', False):
        event_group = Event_Group.objects.get(pk=request_data.get('eventGroupId'))
        events = event_group.events.all()
        event_ids = [event.id for event in events]
        response_data = {'eventGroupId': event_group.id, 'deletedEvents': event_ids}
        for event in events:
            event.delete()
        event_group.delete()
        return HttpResponse(json.dumps(response_data),  content_type="application/json", status= 200)

    event = Event.objects.get(pk=request_data['event_id'])
    event.delete()
    json_data = json.dumps({'event_id':event.id})
    return HttpResponse(json_data,  content_type="application/json", status= 200)


@csrf_exempt
def send_single_invitation(request):
    if not request.method == 'POST':
        return json_error("Method should be POST")

    person = get_person_from_request(request) 
    if not person:
        return logout_view(request)

    request_data = json.loads(request.body)
    response_data = {}

    event = Event.objects.get(pk=request_data['event_id'])
    player = Player.objects.get(pk=request_data['player_id'])
    event_players = Event_Player.objects.filter(event=event, player=player)

    if len(event_players) != 1:
        response_data = {'status':400}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    send_invite_mail(event_players, event)

    event_player = event_players[0]
    event_player.sent = True
    event_player.answer = 4
    event_player.save()
    
    response_data = {'status':200}

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def rsvp_data(request):
    if request.method != 'POST':
        return HttpResponse("Method should be POST",  content_type="application/json", status=400)

    client_data = json.loads(request.body)
    person = get_person_from_request(request)
    if person:
        if len(client_data['event_id']) > 20:
            event_player = Event_Player.objects.get(url_hash=client_data['event_id'])
        else:
            event_player = Event_Player.objects.get(url_hash = generate_url_hash(person.username, client_data['event_id']))
    else:
        try:
            event_player = Event_Player.objects.get(url_hash=client_data['hash'])
        except:
            return HttpResponse(json.dumps({'error': 'Unknown hash'}), content_type="application/json")
    if not event_player.seen:
        event_player.seen = True
        event_player.answer = 3
        event_player.save()

    attendees = Event_Player.objects.filter(event=event_player.event).exclude(player=event_player.player.id)
    attendees_sorted = get_attendees_sorted(attendees)
    attendees_sorted = add_attendee_first(attendees_sorted, event_player)
    event_data = build_json_event(event_player.event)
    event_data['attendees']  = attendees_sorted

    player = {
        'id' : event_player.player.id, 
        'name' : event_player.player.person.first_name, 
        'first_name': event_player.player.person.first_name,
        'last_name': event_player.player.person.last_name, 
        'answer' : event_player.answer, 
        'event_player_id' : event_player.id, 
        'comment' : event_player.comment
        }

    coaches = []
    for event_coach in Event_Coach.objects.filter(event=event_player.event):
        event_coach_dict = {
            'username': event_coach.person.username,
            'firstName': event_coach.person.first_name,
            'lastName': event_coach.person.last_name,
            'answerInt': event_coach.answer
        }
        coaches.append(event_coach_dict)

    ep = {
        'event' : event_data, 
        'player' : player, 
        'attendees' : attendees_sorted,
        'coaches': coaches
        }

    json_data = json.dumps(ep)
    return HttpResponse(json_data,  content_type="application/json")


@csrf_exempt
def rsvp(request):
    if request.method != 'POST':
        return json_error('rsvp not post')

    json_data = json.loads(request.body)
    ep_id = json_data['event_player_id']
    event_player = Event_Player.objects.get(pk=ep_id)

    if json_data.get('answer'):
        event_player.answer = int(json_data['answer'])
    
    if json_data.get('comment'):
        event_player.comment = json_data['comment']
    
    event_player.save()

    #handle case where player is also a coach:
    try:
        event_coach = Event_Coach.objects.get(person=event_player.player.person, event=event_player.event)
        event_coach.answer = event_player.answer
        event_coach.save()
        event_coach_status = 'Event coach updated.'
    except:
       event_coach_status = 'Not event coach.'
  
    attendees = Event_Player.objects.filter(event=event_player.event).exclude(player=event_player.player.id)
    attendees_sorted = get_attendees_sorted(attendees)
    attendees_sorted = add_attendee_first(attendees_sorted, event_player)

    event_coaches = []
    for event_coach in Event_Coach.objects.filter(event=event_player.event):
        event_coach_dict = {
            'username': event_coach.person.username,
            'firstName': event_coach.person.first_name,
            'lastName': event_coach.person.last_name,
            'answerInt': event_coach.answer
        }
        event_coaches.append(event_coach_dict)

    data  = {'answer' : event_player.answer,
             'comment' : event_player.comment,
             'attendees' : attendees_sorted,
             'eventCoachStatus': event_coach_status,
             'coaches': event_coaches}

    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
def rsvp_coach(request):
    if request.method != 'POST':
        return json_error('rsvp not post')

    request_data = json.loads(request.body)
    
    user_person = get_person_from_request(request)
    event = Event.objects.get(pk=request_data.get('eventId'))
    event_coach = Event_Coach.objects.get(person=user_person, event=event)
    answer = request_data.get('answer')
    
    event_coach.answer = answer
    event_coach.save()

    event_player_status = _rsvp_coach_and_player(user_person, event, answer)

    event_coaches = []
    for event_coach in Event_Coach.objects.filter(event=event):
        event_coach_dict = {
            'username': event_coach.person.username,
            'firstName': event_coach.person.first_name,
            'lastName': event_coach.person.last_name,
            'answerInt': event_coach.answer
        }
        event_coaches.append(event_coach_dict)
  
    response_data  = {'answer' : event_coach.answer, 'eventCoaches': event_coaches, 'eventPlayerStatus': event_player_status}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def answer_to_string(answer):
    if answer == 1:
        return "Ja"
    elif answer == 2:
        return "Nei"
    elif answer == 3:
        return "Sett"
    elif answer == 4:
        return "Ikke åpnet"
    else:
        return "Ikke sendt"

def get_dateofbirth(attendee):
    try:
        return attendee.player.person.dateofbirth.strftime("%d/%m/%y")
    except:
        return ""
        

def get_attendees_sorted(attendees, key="answerInt"):
    attendees_list = [{
                    'username': attendee.player.person.username,
                    'firstName': attendee.player.person.first_name,
                    'lastName': attendee.player.person.last_name,
                    'email': attendee.player.person.email,
                    'answer': answer_to_string(attendee.answer),
                    'sent': attendee.sent,
                    'id': attendee.player.id,
                    'answerInt': attendee.answer,
                    'comment': attendee.comment,
                    'dateOfBirth' : get_dateofbirth(attendee),
                    'shirtNumber' : attendee.player.shirt_number,
                    'teamId': attendee.player.team.id,
                    'teamName': attendee.player.team.name,
                } for attendee in attendees]

    attendees_sorted = sorted(attendees_list, key=lambda k: k[key])
    return attendees_sorted

def add_attendee_first(attendees, event_player):
    attendees.insert(0,{
                        'firstName' : event_player.player.person.first_name,
                        'lastName' : event_player.player.person.last_name, 
                        'answer' : answer_to_string(event_player.answer), 
                        'sent' : event_player.sent, 
                        'id' : event_player.player.id,
                        'answerInt' : event_player.answer
                        })
    return attendees


def datetimeformat(datetime):
    datetime = str(datetime)
    splitDT = datetime.split(" ")
    if len(splitDT) > 1:
        date = splitDT[0]
        splitDT = splitDT[1].split(".")
        splitDT = splitDT[0].split(":")
        time = splitDT[0] + ":" + splitDT[1]
        datetimedict = {'date' : date, 'time' : time}
        return datetimedict    
    else:
        return {'date' : '', 'time' : ''}


@csrf_exempt
def return_events_guardian (request):
    if request.method != 'GET':
        return json('not a GET request')

    person = get_person_from_request(request) 
    if not person:
        return logout_view(request)

    players = Player.objects.all()

    children = []

    for player in players:
        if not player.guardians:
            continue
        for guardian in player.guardians.all():
            if person.username == guardian.username:
                children.append(player)

    event_players = []
    for child in children:
        event_players += Event_Player.objects.filter(player=child).exclude(answer=5)

    now = datetime.datetime.now()
    event_list = []

    for event_player in event_players:

        event_datetime = event_player.event.meetup_datetime.replace(tzinfo=None)
        delta = now - event_datetime
        if delta.days > 7 or now > event_datetime:
            continue

        event_data = {
        'id': event_player.event.id,
        'title' : event_player.event.title, 
        'date':datetimeformat(event_player.event.start_datetime)['date'], 
        'startTime':datetimeformat(event_player.event.start_datetime)['time'],
        'meetupTime': datetimeformat(event_player.event.meetup_datetime)['time'],
        'nrOfAttendees': return_nr_ofAttendees_local(event_player.event.id),
        'nfOfNotAttendees': return_nr_of_notAttendees_local(event_player.event.id),
        'dateTime': datetimeformat(event_player.event.start_datetime),
        'sent': is_sent(event_player.event),
        'urlHash': event_player.url_hash,
        'playerName': event_player.player.person.first_name + ' ' + event_player.player.person.last_name,
        'playerAnswerInt': event_player.answer,
        'playerAnswer': answer_to_string(event_player.answer),
        }

        event_list.append(event_data)

    sorted_events_list = sorted(event_list, key=lambda item:item['dateTime'])
    json_data = json.dumps(sorted_events_list)
        
    return HttpResponse(json_data,  content_type="application/json")


@csrf_exempt
def return_events_player (request):
    if request.method != 'GET':
        return json('not a GET request')

    person = get_person_from_request(request) 
    if not person:
        return logout_view(request)

    player_list = Player.objects.filter(person=person)

    event_players = []
    for player in player_list:
        event_players += Event_Player.objects.filter(player=player).exclude(answer=5)

    player_events = []

    now = datetime.datetime.now()

    for event_player in event_players:

        event_datetime = event_player.event.meetup_datetime.replace(tzinfo=None)
        delta = now - event_datetime
        if delta.days > 7 or now > event_datetime:
            continue

        event_player_data = {
        'id': event_player.event.id,
        'title' : event_player.event.title, 
        'date':datetimeformat(event_player.event.start_datetime)['date'], 
        'startTime':datetimeformat(event_player.event.start_datetime)['time'],
        'meetupTime': datetimeformat(event_player.event.meetup_datetime)['time'],
        'nrOfAttendees': return_nr_ofAttendees_local(event_player.event.id),
        'nfOfNotAttendees': return_nr_of_notAttendees_local(event_player.event.id),
        'dateTime': datetimeformat(event_player.event.start_datetime),
        'sent': is_sent(event_player.event),
        'answerInt': event_player.answer,
        'answer': answer_to_string(event_player.answer),
        }

        player_events.append(event_player_data)

    player_events = sorted(player_events, key=lambda item:item['dateTime'])
    json_data = json.dumps(player_events)
        
    return HttpResponse(json_data,  content_type="application/json")
        


def return_nr_ofAttendees_local(event_id):
    nrOfAttendees = Event_Player.objects.filter(event=event_id).filter(answer=1).count()
    return nrOfAttendees


def return_nr_of_notAttendees_local(event_id):
    nrOfNotAttendees = Event_Player.objects.filter(event=event_id).filter(answer=2).count()
    return nrOfNotAttendees


def is_sent(event):
    if Event_Player.objects.filter(event=event,sent=True).count():
        return True
    else: 
        return False


def return_events_list(events):
    events_list = [{
                    'id': event.id,
                    'title' : event.title, 
                    'date':datetimeformat(event.start_datetime)['date'], 
                    'startTime':datetimeformat(event.start_datetime)['time'],
                    'meetupTime': datetimeformat(event.meetup_datetime)['time'],
                    'nrOfAttendees': return_nr_ofAttendees_local(event.id),
                    'nfOfNotAttendees': return_nr_of_notAttendees_local(event.id),
                    'dateTime': datetimeformat(event.start_datetime),
                    'sent': is_sent(event),
                } for event in events]
    sorted_events_list = sorted(events_list, key=lambda item:item['dateTime'])

    miniList = sorted_events_list
    return miniList
