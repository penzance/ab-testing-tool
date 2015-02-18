# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ab_tool', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='notes',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='interventionpoint',
            name='notes',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
