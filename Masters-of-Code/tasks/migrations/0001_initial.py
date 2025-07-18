# Generated by Django 5.2.1 on 2025-05-28 14:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('reminder_type', models.CharField(blank=True, max_length=50)),
                ('notification_method', models.CharField(blank=True, max_length=50)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_closed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
