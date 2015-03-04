# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ab_tool', '0002_auto_20150218_1330'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experimentstudent',
            name='lis_person_sourcedid',
        ),
        migrations.AddField(
            model_name='experimentstudent',
            name='student_name',
            field=models.CharField(max_length=256, null=True, db_index=True),
            preserve_default=True,
        ),
    ]
