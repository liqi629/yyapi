# Generated by Django 3.1.2 on 2020-11-09 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0006_db_apis_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='DB_cases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=10, null=True, verbose_name='所属项目id')),
                ('name', models.CharField(max_length=50, null=True, verbose_name='用例名字')),
            ],
        ),
    ]
