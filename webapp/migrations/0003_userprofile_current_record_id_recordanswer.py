# Generated by Django 4.2.3 on 2023-08-11 11:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webapp', '0002_alter_imageprofile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='current_record_id',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='RecordAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('place', models.CharField(max_length=20)),
                ('mood1', models.CharField(max_length=20)),
                ('mood2', models.CharField(max_length=20)),
                ('mood3', models.CharField(max_length=20)),
                ('q1_mood', models.BooleanField(default=False)),
                ('q2_mood', models.BooleanField(default=False)),
                ('q3_mood', models.BooleanField(default=False)),
                ('rate', models.IntegerField(default=0)),
                ('q1_answer', models.CharField(max_length=200)),
                ('q2_answer', models.CharField(max_length=200)),
                ('q3_answer', models.CharField(max_length=200)),
                ('summary', models.CharField(max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
