# Generated by Django 2.0.6 on 2018-09-22 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0010_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membre',
            name='photo',
            field=models.FileField(help_text='(formats PDF, PNG ou JPEG). ', upload_to='photos', verbose_name="Photo d'identité"),
        ),
    ]
