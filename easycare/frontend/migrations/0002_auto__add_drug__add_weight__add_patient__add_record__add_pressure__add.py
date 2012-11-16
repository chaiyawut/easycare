# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Drug'
        db.create_table('frontend_drug', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.Record'])),
            ('period', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=2, decimal_places=1, blank=True)),
        ))
        db.send_create_signal('frontend', ['Drug'])

        # Adding model 'Weight'
        db.create_table('frontend_weight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.Record'])),
            ('period', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('weight', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('frontend', ['Weight'])

        # Adding model 'Patient'
        db.create_table('frontend_patient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hn', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('contact_number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('frontend', ['Patient'])

        # Adding model 'Record'
        db.create_table('frontend_record', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.Patient'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 11, 15, 0, 0))),
            ('voicemail', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='\xe0\xb8\xa3\xe0\xb8\xad\xe0\xb8\x81\xe0\xb8\xb2\xe0\xb8\xa3\xe0\xb8\x95\xe0\xb8\xad\xe0\xb8\x9a\xe0\xb8\x81\xe0\xb8\xa5\xe0\xb8\xb1\xe0\xb8\x9a', max_length=200)),
        ))
        db.send_create_signal('frontend', ['Record'])

        # Adding model 'Pressure'
        db.create_table('frontend_pressure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontend.Record'])),
            ('period', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('up', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('down', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('frontend', ['Pressure'])

        # Adding model 'Response'
        db.create_table('frontend_response', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('record', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['frontend.Record'], unique=True)),
            ('nurse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('reply_text', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('frontend', ['Response'])


    def backwards(self, orm):
        # Deleting model 'Drug'
        db.delete_table('frontend_drug')

        # Deleting model 'Weight'
        db.delete_table('frontend_weight')

        # Deleting model 'Patient'
        db.delete_table('frontend_patient')

        # Deleting model 'Record'
        db.delete_table('frontend_record')

        # Deleting model 'Pressure'
        db.delete_table('frontend_pressure')

        # Deleting model 'Response'
        db.delete_table('frontend_response')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'frontend.drug': {
            'Meta': {'object_name': 'Drug'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '2', 'decimal_places': '1', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Record']"}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'frontend.patient': {
            'Meta': {'object_name': 'Patient'},
            'contact_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'hn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'frontend.pressure': {
            'Meta': {'object_name': 'Pressure'},
            'down': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Record']"}),
            'up': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'frontend.record': {
            'Meta': {'object_name': 'Record'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 15, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Patient']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'\\xe0\\xb8\\xa3\\xe0\\xb8\\xad\\xe0\\xb8\\x81\\xe0\\xb8\\xb2\\xe0\\xb8\\xa3\\xe0\\xb8\\x95\\xe0\\xb8\\xad\\xe0\\xb8\\x9a\\xe0\\xb8\\x81\\xe0\\xb8\\xa5\\xe0\\xb8\\xb1\\xe0\\xb8\\x9a'", 'max_length': '200'}),
            'voicemail': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'frontend.response': {
            'Meta': {'object_name': 'Response'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nurse': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'record': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['frontend.Record']", 'unique': 'True'}),
            'reply_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'frontend.weight': {
            'Meta': {'object_name': 'Weight'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Record']"}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'})
        }
    }

    complete_apps = ['frontend']