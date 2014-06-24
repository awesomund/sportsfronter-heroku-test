# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Team'
        db.create_table(u'event_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'event', ['Team'])

        # Adding model 'Person'
        db.create_table(u'event_person', (
            (u'user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('dateofbirth', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'event', ['Person'])

        # Adding M2M table for field coach_roles on 'Person'
        m2m_table_name = db.shorten_name(u'event_person_coach_roles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm[u'event.person'], null=False)),
            ('team', models.ForeignKey(orm[u'event.team'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'team_id'])

        # Adding model 'Player'
        db.create_table(u'event_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Person'])),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Team'])),
            ('shirt_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'event', ['Player'])

        # Adding M2M table for field guardians on 'Player'
        m2m_table_name = db.shorten_name(u'event_player_guardians')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('player', models.ForeignKey(orm[u'event.player'], null=False)),
            ('person', models.ForeignKey(orm[u'event.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['player_id', 'person_id'])

        # Adding model 'Event'
        db.create_table(u'event_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('meetup_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('start_datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Team'])),
            ('opponent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='opponent', null=True, to=orm['event.Team'])),
        ))
        db.send_create_signal(u'event', ['Event'])

        # Adding model 'Event_Player'
        db.create_table(u'event_event_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Player'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Event'])),
            ('url_hash', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('seen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('answer', self.gf('django.db.models.fields.IntegerField')()),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'event', ['Event_Player'])

        # Adding model 'Device'
        db.create_table(u'event_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Person'])),
            ('registration_id', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal(u'event', ['Device'])


    def backwards(self, orm):
        # Deleting model 'Team'
        db.delete_table(u'event_team')

        # Deleting model 'Person'
        db.delete_table(u'event_person')

        # Removing M2M table for field coach_roles on 'Person'
        db.delete_table(db.shorten_name(u'event_person_coach_roles'))

        # Deleting model 'Player'
        db.delete_table(u'event_player')

        # Removing M2M table for field guardians on 'Player'
        db.delete_table(db.shorten_name(u'event_player_guardians'))

        # Deleting model 'Event'
        db.delete_table(u'event_event')

        # Deleting model 'Event_Player'
        db.delete_table(u'event_event_player')

        # Deleting model 'Device'
        db.delete_table(u'event_device')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'event.device': {
            'Meta': {'object_name': 'Device'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Person']"}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'event.event': {
            'Meta': {'object_name': 'Event'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'meetup_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'opponent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'opponent'", 'null': 'True', 'to': u"orm['event.Team']"}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Team']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'event.event_player': {
            'Meta': {'object_name': 'Event_Player'},
            'answer': ('django.db.models.fields.IntegerField', [], {}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Player']"}),
            'seen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url_hash': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'event.person': {
            'Meta': {'object_name': 'Person', '_ormbases': [u'auth.User']},
            'coach_roles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['event.Team']", 'null': 'True', 'blank': 'True'}),
            'dateofbirth': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'event.player': {
            'Meta': {'object_name': 'Player'},
            'guardians': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'guardian'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['event.Person']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Person']"}),
            'shirt_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['event.Team']"})
        },
        u'event.team': {
            'Meta': {'object_name': 'Team'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['event']