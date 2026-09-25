from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comunication', '0011_read_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='read',
            name='video',
        ),
    ]
