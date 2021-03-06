# Generated by Django 2.0.6 on 2019-08-25 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0015_remove_licence_num_licence'),
    ]

    operations = [
        migrations.AddField(
            model_name='paiement',
            name='stripe_intent',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='membre',
            name='num_licence',
            field=models.CharField(blank=True, help_text='Si vous avez déjà été licencié et que vous le connaissez', max_length=15, verbose_name='Numéro de licence'),
        ),
    ]
