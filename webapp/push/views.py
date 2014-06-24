 #!/usr/bin/python
 # -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from event.models import Player, Event, Event_Player, Device
from auth.views import get_person_from_request

# Needed by send_push_message
import urllib2
import json
import logging
import socket
import ssl
import struct
import datetime

logger = logging.getLogger("sportsfronter.push.views")


def _count_notifications(person):
    # Counts number of unanswered events for a user.
    # Both events where a user is a player, and events where the user
    # is a guardian for a player.
    notifications = 0

    players = person.player_set.all()
    for player in players:
        event_players = Event_Player.objects.filter(player=player, answer=4)
        for event_player in event_players:
            if event_player.event.start_datetime.replace(tzinfo=None) >= datetime.datetime.now():
                notifications += 1

    guardian_roles = person.guardian.all()
    for guardian_role in guardian_roles:
        event_players = Event_Player.objects.filter(player=guardian_role, answer=4)
        for event_player in event_players:
            if event_player.event.start_datetime.replace(tzinfo=None) >= datetime.datetime.now():
                notifications += 1

    return notifications


def count_notifications(request):
    person = get_person_from_request(request)
    if not person:
        return HttpResponse(json.dumps({'person': None}, status=400))

    return HttpResponse(json.dumps({'notifications': _count_notifications(person)}))


def create_request_data_dict(title, message, recipients, event_id):
    data = {"registration_ids": recipients, "data": {"title": title, "message": message, "event_id": event_id}}
    return json.dumps(data)


def send_push_message_android(title, message, recipients, event_id):
    # Specify the address for Androids GCM server
    url = 'https://android.googleapis.com/gcm/send'
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'key=AIzaSyBJ6uTxUs9QAAgN34AryaVI68uu2hKIdPg'
    }
    data = create_request_data_dict(title, message, recipients, event_id)

    # Send request
    request = urllib2.Request(url, data, headers)
    f = urllib2.urlopen(request)


def index(request):
    groups = Group.objects.all()
    return render(request, 'push/index.html', {'groups':groups})


def send_push_message_ios(title, message, url_hash, ios_registration_ids):
    logger.info('Sending push message for ios')
    certificate_file = settings.SSL_APPLE_DEV_CERTIFICATE_PATH
    ios_hostname = ('gateway.push.apple.com', 2195)

    # Developer hostname, change for testing locally
    # ios_hostname = ('gateway.sandbox.push.apple.com', 2195)


    # Create our connection using the certfile saved locally
    ssl_sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), certfile=certificate_file)
    ssl_sock.connect(ios_hostname)


    for deviceToken in ios_registration_ids:
        payload = {
            'aps': {
                'alert': message,
                'sound': 'k1DiveAlarm.caf',
                'badge': 1,
            },
            'eventurl': 'https://sportsfronter.iterate.no/#/rsvp/' + url_hash,
        }

        data = json.dumps(payload)

        # Clear out spaces in the device token and convert to hex
        deviceToken = deviceToken.replace(' ', '')
        byteToken = deviceToken.decode('hex') # Python 2

        theFormat = '!BH32sH%ds' % len(data)
        theNotification = struct.pack(theFormat, 0, 32, byteToken, len(data), data)


        # Write out our data
        ssl_sock.write(theNotification)

        # Close the connection -- apple would prefer that we keep
        # a connection open and push data as needed.
    ssl_sock.close()

def submit(request):
    if request.method == 'POST':
        title = request.POST['title']
        message = request.POST['message']
        group_id = request.POST['group']
        group = Group.objects.get(id=group_id)
        group_members = group.user_set.all()
        # Unique ID that tells Google where to send the push message
        android_registration_ids = []
        ios_registration_ids = []
        for member in group_members:
            devices = member.device_set.all()
            for device in devices:
                if (device.device_type is 'android'):
                    android_registration_ids.append(device.registration_id)
                else:
                    ios_registration_ids.append(device.registration_id)

        send_push_message_android(title, message, android_registration_ids)
        send_push_message_ios(title, message, ios_registration_ids)


        context = {
            'title': title,
            'message': message,
            'group': group
        }
        return render(request, 'push/success.html', context)

    return render(request, 'push/success.html')
    # return redirect('/success/')


def success(request):
    return render(request, 'push/success.html')


def push_out_new_events(player, event, msg_type, event_url_hash):
    try:
        logger.info("Starting to send push messages for: " + player.person.username + ", " + event.title)

        devices = Device.objects.filter(owner=player.person)

        if not devices:
            logger.info("No devices for this player.")

        msg = push_message_generator(msg_type,event)

        for device in devices:
            if device.device_type == 'android':
                send_push_message_android(event.title, msg, [device.registration_id], event.id)
                logger.info("Sent push message to player (android): " + event.title + ", " + player.person.username)
            else:
                send_push_message_ios(event.title, msg, event_url_hash, [device.registration_id])
                logger.info("Sent push message to player (ios): " + event.title + ", " + player.person.username)
        for guardian in player.guardians.all():
            devicesGuardians = Device.objects.filter(owner=guardian)
            if not devicesGuardians:
                logger.info("No devices for guardian " + guardian.username)
            for device in devicesGuardians:
                if device.device_type == 'android':
                    send_push_message_android(event.title, msg, [device.registration_id], event.id)
                    logger.info("Sent push message to player (ios): " + event.title + ", " + player.person.username)
                else:
                    send_push_message_ios(event.title, msg, event_url_hash, [device.registration_id])
                    logger.info("Sent push message to guardian (ios): " + event.title + ", " + player.person.username)

        logger.info("""Successfully sent push messages (if any) regarding: """
                    + player.person.username + """, """
                    + player.person.first_name + """ """ + player.person.last_name + """, """ + event.title)

    except Exception, err:
        logger.debug("Got exception when trying to push out new events")
        logger.exception(err)
        pass
        # print "No device id save in db"


def format_time(time):
    return time.strftime('%H:%M')


def format_date(date):
    return date.strftime('%d/%m/%Y')


def push_message_generator(msg_type, event):
    message =""
    if msg_type == "invite":
        message = "Du er invitert til %s som starter klokken: %s den %s" % (str(event.title.encode('utf-8')), format_time(event.start_datetime),
            format_date(event.meetup_datetime))
    elif msg_type == "update":
        message = "Det har skjedd en oppdatering i %s, trykk her for å se den" % (event.title.encode('utf-8'))
    elif msg_type == "reminder":
        message = "Du må huske å svare på %s som skjer den %s" %(str(event.title.encode('utf-8')), format_date(event.meetup_datetime))

    logger.info("Successfully generated push message for " + event.title.encode('utf-8'))
    return message






