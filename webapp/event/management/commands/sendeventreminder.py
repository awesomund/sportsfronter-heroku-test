from django.core.management.base import BaseCommand
from event.models import Event, Event_Player
import datetime

from event.email_utils import send_reminder_mail
from push.views import push_out_new_events

#Sends event reminder 2 days before event

# Class MUST be named 'Command'
class Command(BaseCommand):

    # Displayed from 'manage.py help mycommand'
    help = "Sends reminder to all event players when an event is drawing near."

    def handle(self, *app_labels, **options):

        # Return a success message to display to the user on success
        # or raise a CommandError as a failure condition

        events = Event.objects.filter(first_reminder_sent=False, two_hour_reminder_sent=False)
        current_time = datetime.datetime.now()

        print current_time

        for event in events:

            if event.reminder_time == 0:
                continue

            if event.last_signup_datetime is None:
                send_reminder_datetime = event.meetup_datetime.replace(tzinfo=None)
            else:
                send_reminder_datetime = event.last_signup_datetime.replace(tzinfo=None)

            time_delta = send_reminder_datetime - current_time
            hours = time_delta.seconds//3600

            if time_delta.days > event.reminder_time or time_delta.days < 0:
                continue

            if time_delta.days == 0 and hours <= 2:
                event.two_hour_reminder_sent = True
                event.save()
                continue

            event_players = Event_Player.objects.filter(event=event, answer__in=[3,4,5])
            send_reminder_mail(event_players, event)

            for event_player in event_players:
                push_out_new_events(event_player.player, event, 'reminder', event_player.url_hash)
            
            event.first_reminder_sent = True
            event.save()

            print 'Reminder sent: ' + event.title
            print current_time
            print time_delta


        return 'Finished.'