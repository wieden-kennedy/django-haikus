# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'HaikuModel.heat'
        db.add_column('django_haikus_haikumodel', 'heat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding index on 'HaikuModel', fields ['is_composite']
        db.create_index('django_haikus_haikumodel', ['is_composite'])

        # Adding index on 'HaikuModel', fields ['quality']
        db.create_index('django_haikus_haikumodel', ['quality'])


    def backwards(self, orm):
        
        # Removing index on 'HaikuModel', fields ['quality']
        db.delete_index('django_haikus_haikumodel', ['quality'])

        # Removing index on 'HaikuModel', fields ['is_composite']
        db.delete_index('django_haikus_haikumodel', ['is_composite'])

        # Deleting field 'HaikuModel.heat'
        db.delete_column('django_haikus_haikumodel', 'heat')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'django_haikus.haikuline': {
            'Meta': {'ordering': "('line_number',)", 'object_name': 'HaikuLine'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_number': ('django.db.models.fields.IntegerField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'quality': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'django_haikus.haikumodel': {
            'Meta': {'object_name': 'HaikuModel'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'haiku_source'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_text': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True'}),
            'heat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_composite': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'lines': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['django_haikus.HaikuLine']", 'symmetrical': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quality': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'})
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
