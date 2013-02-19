# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Log.created'
        db.alter_column('frontend_log', 'created', self.gf('django.db.models.fields.DateField')(auto_now_add=True))

        # Changing field 'Record.datetime'
        db.alter_column('frontend_record', 'datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))
        # Adding field 'Response.timestamp'
        db.add_column('frontend_response', 'timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2013, 2, 19, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'Log.created'
        db.alter_column('frontend_log', 'created', self.gf('django.db.models.fields.DateField')())

        # Changing field 'Record.datetime'
        db.alter_column('frontend_record', 'datetime', self.gf('django.db.models.fields.DateTimeField')())
        # Deleting field 'Response.timestamp'
        db.delete_column('frontend_response', 'timestamp')


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
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Record']"}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'frontend.log': {
            'Meta': {'object_name': 'Log'},
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sms_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'frontend.patient': {
            'Meta': {'object_name': 'Patient'},
            'confirm_by': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'contact_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'hn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'sound_for_name': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        },
        'frontend.pressure': {
            'Meta': {'object_name': 'Pressure'},
            'down': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Record']"}),
            'up': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'frontend.record': {
            'Meta': {'object_name': 'Record'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Patient']"}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'\\xe0\\xb8\\xa3\\xe0\\xb8\\xad\\xe0\\xb8\\x81\\xe0\\xb8\\xb2\\xe0\\xb8\\xa3\\xe0\\xb8\\x95\\xe0\\xb8\\xad\\xe0\\xb8\\x9a\\xe0\\xb8\\x81\\xe0\\xb8\\xa5\\xe0\\xb8\\xb1\\xe0\\xb8\\x9a'", 'max_length': '200'}),
            'submitted_by': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'voicemail': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'frontend.response': {
            'Meta': {'object_name': 'Response'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nurse': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'record': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['frontend.Record']", 'unique': 'True'}),
            'reply_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'frontend.sign': {
            'Meta': {'object_name': 'Sign'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Record']"}),
            'sign': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'frontend.visit': {
            'Meta': {'object_name': 'Visit'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Patient']"}),
            'visit_type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'frontend.weight': {
            'Meta': {'object_name': 'Weight'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Record']"}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '1', 'blank': 'True'})
        }
    }

    complete_apps = ['frontend']