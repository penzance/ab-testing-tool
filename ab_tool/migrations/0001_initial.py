# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('course_id', models.CharField(max_length=128, db_index=True)),
                ('name', models.CharField(max_length=256)),
                ('notes', models.CharField(max_length=1024)),
                ('tracks_finalized', models.BooleanField(default=False)),
                ('assignment_method', models.IntegerField(default=1, max_length=1, choices=[(1, b'uniform_random'), (2, b'weighted_probability_random'), (3, b'csv_upload'), (4, b'reverse_api')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExperimentStudent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('course_id', models.CharField(max_length=128, db_index=True)),
                ('student_id', models.CharField(max_length=128, db_index=True)),
                ('lis_person_sourcedid', models.CharField(max_length=128, null=True, db_index=True)),
                ('experiment', models.ForeignKey(related_name='students', to='ab_tool.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InterventionPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('course_id', models.CharField(max_length=128, db_index=True)),
                ('name', models.CharField(max_length=256)),
                ('notes', models.CharField(max_length=1024)),
                ('experiment', models.ForeignKey(related_name='intervention_points', to='ab_tool.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InterventionPointInteraction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('course_id', models.CharField(max_length=128, db_index=True)),
                ('url', models.URLField(max_length=2048)),
                ('experiment', models.ForeignKey(related_name='intervention_point_interactions', to='ab_tool.Experiment')),
                ('intervention_point', models.ForeignKey(to='ab_tool.InterventionPoint')),
                ('student', models.ForeignKey(to='ab_tool.ExperimentStudent')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InterventionPointUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('url', models.URLField(max_length=2048)),
                ('open_as_tab', models.BooleanField(default=False)),
                ('is_canvas_page', models.BooleanField(default=False)),
                ('intervention_point', models.ForeignKey(to='ab_tool.InterventionPoint')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('course_id', models.CharField(max_length=128, db_index=True)),
                ('name', models.CharField(max_length=256)),
                ('experiment', models.ForeignKey(related_name='tracks', to='ab_tool.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrackProbabilityWeight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('course_id', models.CharField(max_length=128, db_index=True)),
                ('weighting', models.IntegerField()),
                ('experiment', models.ForeignKey(related_name='track_probabilites', to='ab_tool.Experiment')),
                ('track', models.OneToOneField(related_name='weight', to='ab_tool.Track')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='track',
            unique_together=set([('experiment', 'name')]),
        ),
        migrations.AddField(
            model_name='interventionpointurl',
            name='track',
            field=models.ForeignKey(to='ab_tool.Track'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='interventionpointurl',
            unique_together=set([('track', 'intervention_point')]),
        ),
        migrations.AddField(
            model_name='interventionpointinteraction',
            name='track',
            field=models.ForeignKey(to='ab_tool.Track'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='interventionpoint',
            name='tracks',
            field=models.ManyToManyField(to='ab_tool.Track', through='ab_tool.InterventionPointUrl'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='interventionpoint',
            unique_together=set([('experiment', 'name')]),
        ),
        migrations.AddField(
            model_name='experimentstudent',
            name='track',
            field=models.ForeignKey(to='ab_tool.Track'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='experimentstudent',
            unique_together=set([('experiment', 'student_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='experiment',
            unique_together=set([('course_id', 'name')]),
        ),
    ]
