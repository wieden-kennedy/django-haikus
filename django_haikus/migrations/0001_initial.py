# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'HaikuRating'
        db.create_table('django_haikus_haikurating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('django_haikus', ['HaikuRating'])

        # Adding model 'HaikuModel'
        db.create_table('django_haikus_haikumodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lines', self.gf('picklefield.fields.PickledObjectField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='haikus', null=True, to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('quality', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('django_haikus', ['HaikuModel'])

        # Adding unique constraint on 'HaikuModel', fields ['lines', 'object_id']
        db.create_unique('django_haikus_haikumodel', ['lines', 'object_id'])

        # Adding model 'SimpleText'
        db.create_table('django_haikus_simpletext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('syllables', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_haiku', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('django_haikus', ['SimpleText'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'HaikuModel', fields ['lines', 'object_id']
        db.delete_unique('django_haikus_haikumodel', ['lines', 'object_id'])

        # Deleting model 'HaikuRating'
        db.delete_table('django_haikus_haikurating')

        # Deleting model 'HaikuModel'
        db.delete_table('django_haikus_haikumodel')

        # Deleting model 'SimpleText'
        db.delete_table('django_haikus_simpletext')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'django_haikus.haikumodel': {
            'Meta': {'unique_together': "(('lines', 'object_id'),)", 'object_name': 'HaikuModel'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'haikus'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lines': ('picklefield.fields.PickledObjectField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quality': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'django_haikus.haikurating': {
            'Meta': {'object_name': 'HaikuRating'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'django_haikus.simpletext': {
            'Meta': {'object_name': 'SimpleText'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_haiku': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'syllables': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['django_haikus']
