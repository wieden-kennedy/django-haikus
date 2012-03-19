# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'HaikuModel.up_votes'
        db.add_column('django_haikus_haikumodel', 'up_votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)

        # Adding field 'HaikuModel.down_votes'
        db.add_column('django_haikus_haikumodel', 'down_votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'HaikuModel.up_votes'
        db.delete_column('django_haikus_haikumodel', 'up_votes')

        # Deleting field 'HaikuModel.down_votes'
        db.delete_column('django_haikus_haikumodel', 'down_votes')


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
            'down_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lines': ('picklefield.fields.PickledObjectField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quality': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'up_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
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
