from django.db import migrations

def add_invite_id_field(apps, schema_editor):
    # Добавляем поле invite_id к auth_user без UNIQUE
    schema_editor.execute(
        "ALTER TABLE auth_user ADD COLUMN invite_id varchar(32)"
    )

class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0005_task_description_task_points_task_trigger_task_and_more'),
    ]
    operations = [
        migrations.RunPython(add_invite_id_field),
    ] 