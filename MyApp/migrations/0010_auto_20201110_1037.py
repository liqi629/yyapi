# Generated by Django 3.1.2 on 2020-11-10 02:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0009_auto_20201110_1037'),
    ]

    operations = [
        migrations.RenameField(
            model_name='db_step',
            old_name='case_id',
            new_name='Case_id',
        ),
    ]
