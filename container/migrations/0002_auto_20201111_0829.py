# Generated by Django 3.0.3 on 2020-11-11 08:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('container', '0001_initial'),
        ('vm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='new_docker_apply',
            name='regionID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vm.domain'),
        ),
        migrations.AddField(
            model_name='new_docker_apply',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='docker_node',
            name='belong',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vm.domain'),
        ),
        migrations.AddField(
            model_name='container',
            name='img',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='container.docker_img'),
        ),
        migrations.AddField(
            model_name='container',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='container.docker_node'),
        ),
        migrations.AddField(
            model_name='container',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vm.domain'),
        ),
        migrations.AddField(
            model_name='container',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
