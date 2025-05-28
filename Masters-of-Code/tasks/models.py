from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

# Добавляем поле friends к User через monkey patch
if not hasattr(User, 'friends'):
    User.add_to_class('friends', models.ManyToManyField('self', symmetrical=False, related_name='friend_of', blank=True))
# Добавляем поле position (роль) и is_ceo (Ген директор)
if not hasattr(User, 'position'):
    User.add_to_class('position', models.CharField(max_length=100, blank=True, verbose_name='Должность'))
if not hasattr(User, 'is_ceo'):
    User.add_to_class('is_ceo', models.BooleanField(default=False, verbose_name='Генеральный директор'))
# Добавляем first_name, last_name, avatar
if not hasattr(User, 'first_name'):
    User.add_to_class('first_name', models.CharField(max_length=150, blank=True, verbose_name='Имя'))
if not hasattr(User, 'last_name'):
    User.add_to_class('last_name', models.CharField(max_length=150, blank=True, verbose_name='Фамилия'))
if not hasattr(User, 'avatar'):
    User.add_to_class('avatar', models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар'))
if not hasattr(User, 'invite_id'):
    User.add_to_class('invite_id', models.CharField(max_length=32, unique=True, blank=True, null=True, verbose_name='Invite ID'))

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, verbose_name='Описание')
    due_date = models.DateTimeField(null=True, blank=True)
    REMINDER_CHOICES = [
        ('none', 'Нет'),
        ('one_time', 'Однократное'),
        ('periodic', 'Периодическое'),
        ('daily', 'Ежедневное'),
        ('trigger', 'По триггеру'),
    ]
    reminder_type = models.CharField(max_length=50, blank=True, choices=REMINDER_CHOICES, default='none')
    NOTIFY_CHOICES = [
        ('none', 'Нет'),
        ('email', 'Email'),
        ('sms', 'СМС'),
        ('push', 'Push Notification'),
    ]
    notification_method = models.CharField(max_length=50, blank=True, choices=NOTIFY_CHOICES, default='none')
    points = models.IntegerField(default=0, verbose_name='Очки за выполнение')
    is_completed = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trigger_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Триггер-задача')

    def __str__(self):
        return self.title
