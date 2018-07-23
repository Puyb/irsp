# Generated by Django 2.0.6 on 2018-07-22 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membre',
            name='num_licence',
        ),
        migrations.RemoveField(
            model_name='membre',
            name='photo_valide',
        ),
        migrations.AddField(
            model_name='licence',
            name='num_licence',
            field=models.CharField(blank=True, help_text='Si vous le connaissez', max_length=15, verbose_name='Numéro de licence'),
        ),
        migrations.AlterField(
            model_name='licence',
            name='certificat',
            field=models.FileField(blank=True, help_text='Votre certificat médical doit dater de moins de 1 ans et doit mentionner que vous êtes "aptes à la pratique du roller" et "en compétition" si vous souhaitez faire des compétitions. Si vous le pouvez, scannez le certificat et ajoutez le (formats PDF ou JPEG).', upload_to='certificats', verbose_name='Certificat médical'),
        ),
        migrations.AlterField(
            model_name='licence',
            name='certificat_valide',
            field=models.BooleanField(default=False, verbose_name='Certificat valide'),
        ),
        migrations.AlterField(
            model_name='membre',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=200, verbose_name="E-mail d'un contact en cas d'urgence"),
        ),
        migrations.AlterField(
            model_name='membre',
            name='contact_nom',
            field=models.CharField(help_text='Personne a contacter en cas de problème ou responsable légale pour un mineur', max_length=200, verbose_name="Nom d'un contact en cas d'urgence"),
        ),
        migrations.AlterField(
            model_name='membre',
            name='contact_telephone',
            field=models.CharField(max_length=200, verbose_name="Téléphone d'un contact en cas d'urgence"),
        ),
        migrations.AlterField(
            model_name='membre',
            name='photo',
            field=models.FileField(blank=True, help_text='Si vous le pouvez, ajoutez la photo (formats JPEG). ', upload_to='photos', verbose_name="Photo d'identité"),
        ),
    ]