# Generated by Django 2.0.6 on 2019-08-26 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0019_merge_20190826_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='licence',
            name='cerfa_non',
            field=models.BooleanField(default=False, verbose_name="Je certifie sur l'honneur avoir renseigné le questionnaire de santé QS-SPORT Cerfa N°15699*01 et avoir répondu par la négative à l’ensemble des questions"),
        ),
    ]
