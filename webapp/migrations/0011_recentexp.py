# Generated by Django 4.2.3 on 2023-08-27 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_recordanswer_recent'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecentExp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(blank=True, max_length=20, null=True)),
                ('date', models.DateField(null=True)),
                ('content', models.CharField(max_length=200)),
            ],
        ),
    ]
