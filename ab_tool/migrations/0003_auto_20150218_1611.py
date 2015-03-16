# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ab_tool', '0002_auto_20150218_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=2048)),
                ('token', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('course_id', models.CharField(unique=True, max_length=128)),
                ('last_emailed', models.DateTimeField(null=True)),
                ('canvas_url', models.URLField(max_length=2048)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='coursecredential',
            name='course',
            field=models.ForeignKey(related_name='credentials', to='ab_tool.CourseNotification'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='coursecredential',
            unique_together=set([('course', 'email')]),
        ),
    ]
