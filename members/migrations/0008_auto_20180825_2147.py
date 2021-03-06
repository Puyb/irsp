# Generated by Django 2.0.6 on 2018-08-25 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0007_auto_20180820_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='licence',
            name='cerfa_non',
            field=models.BooleanField(default=False, verbose_name="Je certifie sur l'honneur avoir renseigner le questionnaire de santé QS-SPORT Cerfa N°15699*01 et avoir répondu par la négative à l’ensemble des questions"),
        ),
        migrations.AlterField(
            model_name='licence',
            name='certificat',
            field=models.FileField(blank=True, help_text='Votre certificat médical doit dater de moins de 1 ans et doit mentionner que vous êtes "aptes à la pratique du roller" et "en compétition" si vous souhaitez faire des compétitions. Si vous le pouvez, scannez le certificat et ajoutez le (formats PDF ou JPEG).', null=True, upload_to='certificats', verbose_name='Certificat médical'),
        ),
    ]
