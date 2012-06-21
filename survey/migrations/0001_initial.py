# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Survey'
        db.create_table('survey_survey', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=1024, primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('survey', ['Survey'])

        # Adding model 'Question'
        db.create_table('survey_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Survey'])),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('survey', ['Question'])

        # Adding model 'Choice'
        db.create_table('survey_choice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'])),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('survey', ['Choice'])

        # Adding model 'Answer'
        db.create_table('survey_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Choice'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('survey', ['Answer'])


    def backwards(self, orm):
        # Deleting model 'Survey'
        db.delete_table('survey_survey')

        # Deleting model 'Question'
        db.delete_table('survey_question')

        # Deleting model 'Choice'
        db.delete_table('survey_choice')

        # Deleting model 'Answer'
        db.delete_table('survey_answer')


    models = {
        'survey.answer': {
            'Meta': {'object_name': 'Answer'},
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Choice']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'survey.choice': {
            'Meta': {'object_name': 'Choice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']"})
        },
        'survey.question': {
            'Meta': {'object_name': 'Question'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Survey']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'survey.survey': {
            'Meta': {'object_name': 'Survey'},
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '1024', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['survey']