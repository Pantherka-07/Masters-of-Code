from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['trigger_task'].queryset = Task.objects.filter(user=user)
        else:
            self.fields['trigger_task'].queryset = Task.objects.none()

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'reminder_type', 'notification_method', 'points', 'trigger_task']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'reminder_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('none', 'None'),
                ('email', 'Email'),
                ('push', 'Push Notification'),
            ]),
            'notification_method': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('none', 'None'),
                ('email', 'Email'),
                ('push', 'Push Notification'),
            ]),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'trigger_task': forms.Select(attrs={'class': 'form-control'}),
        }