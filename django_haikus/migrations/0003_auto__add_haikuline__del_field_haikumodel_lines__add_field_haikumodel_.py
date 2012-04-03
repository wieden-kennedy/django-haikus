# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'HaikuModel', fields ['lines', 'object_id']
        db.delete_unique('django_haikus_haikumodel', ['lines', 'object_id'])

        # Adding model 'HaikuLine'
        db.create_table('django_haikus_haikuline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('line_number', self.gf('django.db.models.fields.IntegerField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('quality', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('django_haikus', ['HaikuLine'])

        # Deleting field 'HaikuModel.lines'
        db.delete_column('django_haikus_haikumodel', 'lines')

        # Adding field 'HaikuModel.is_composite'
        db.add_column('django_haikus_haikumodel', 'is_composite', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding M2M table for field lines on 'HaikuModel'
        db.create_table('django_haikus_haikumodel_lines', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('haikumodel', models.ForeignKey(orm['django_haikus.haikumodel'], null=False)),
            ('haikuline', models.ForeignKey(orm['django_haikus.haikuline'], null=False))
        ))
        db.create_unique('django_haikus_haikumodel_lines', ['haikumodel_id', 'haikuline_id'])


    def backwards(self, orm):
        
        # Deleting model 'HaikuLine'
        db.delete_table('django_haikus_haikuline')

        # Adding field 'HaikuModel.lines'
        db.add_column('django_haikus_haikumodel', 'lines', self.gf('picklefield.fields.PickledObjectField')(default=''), keep_default=False)

        # Deleting field 'HaikuModel.is_composite'
        db.delete_column('django_haikus_haikumodel', 'is_composite')

        # Removing M2M table for field lines on 'HaikuModel'
        db.delete_table('django_haikus_haikumodel_lines')

        # Adding unique constraint on 'HaikuModel', fields ['lines', 'object_id']
        db.create_unique('django_haikus_haikumodel', ['lines', 'object_id'])


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'django_haikus.haikuline': {
            'Meta': {'object_name': 'HaikuLine'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_number': ('django.db.models.fields.IntegerField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'quality': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'django_haikus.haikumodel': {
            'Meta': {'object_name': 'HaikuModel'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'haikus'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'down_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_composite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lines': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['django_haikus.HaikuLine']", 'symmetrical': 'False'}),
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
