# Generated by Django 2.0.6 on 2019-08-25 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0017_remove_pinax_stripe_tables'),
    ]

    operations = [
        migrations.AddField(
            model_name='paiement',
            name='detail',
            field=models.TextField(blank=True),
        ),
    ]
