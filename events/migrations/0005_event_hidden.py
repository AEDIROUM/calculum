# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_event_is_active_event_server_port_event_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='hidden',
            field=models.BooleanField(default=False, help_text='Hide this event from the public events page'),
        ),
    ]
