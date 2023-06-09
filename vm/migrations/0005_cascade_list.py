# Generated by Django 3.0.3 on 2021-05-11 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vm', '0004_vm_available'),
    ]

    operations = [
        migrations.CreateModel(
            name='cascade_list',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('port', models.IntegerField()),
                ('is_communicate', models.BooleanField(default=False, help_text='false: no communicate; true: communicate', null=True)),
                ('is_self', models.BooleanField(default=False, help_text='false: is not the ip of mine, true: is the ip of mine')),
                ('is_master', models.BooleanField(default=False, help_text='false: is not the master of the cascade, true: is the master of the cascade', null=True)),
            ],
        ),
    ]
