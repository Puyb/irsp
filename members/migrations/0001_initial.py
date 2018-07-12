# Generated by Django 2.0.6 on 2018-06-23 15:26

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Licence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reduction', models.CharField(choices=[('actif', 'Actif ou retraité'), ('enfant', 'Enfant'), ('etudiant', 'Étudiant'), ('chomeur', 'Chômeur')], default='actif', max_length=20, verbose_name='Réduction')),
                ('autre_club', models.BooleanField(default=False, verbose_name="J'ai une licence dans un autre club et je souhaite rester licencié dans ce club.")),
                ('discipline', models.CharField(choices=[('rando init', 'Randonnée initiation'), ('Roller Freestyle', 'Slalom'), ('Course', 'Course')], max_length=20, verbose_name='Discipline')),
                ('certificat', models.FileField(blank=True, help_text='Votre certificat médical doit dater de moins de 1 ans et doit mentionner que vous êtes "aptes à la pratique du roller" et "en compétition" si vous souhaitez faire des compétitions. Si vous le pouvez, scannez le certificat et ajoutez le (formats PDF ou JPEG). ', upload_to='certificats', verbose_name='Certificat médical')),
                ('certificat_valide', models.NullBooleanField(verbose_name='Certificat valide')),
                ('paiement_info', models.CharField(blank=True, max_length=1000, verbose_name='Détails')),
                ('prix', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5, verbose_name='Prix')),
                ('paiement', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Paiement reçu')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name="Date d'insciption")),
                ('ffrs', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Membre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200, verbose_name='Nom')),
                ('prenom', models.CharField(blank=True, max_length=200, verbose_name='Prénom')),
                ('sexe', models.CharField(choices=[('H', 'Homme'), ('F', 'Femme')], max_length=1, verbose_name='Sexe')),
                ('adresse1', models.CharField(blank=True, max_length=200, verbose_name='Adresse')),
                ('adresse2', models.CharField(blank=True, max_length=200, verbose_name='Adresse')),
                ('ville', models.CharField(max_length=200)),
                ('code_postal', models.CharField(max_length=200)),
                ('telephone', models.CharField(max_length=200)),
                ('date_de_naissance', models.DateField(verbose_name='Date de naissance')),
                ('num_licence', models.CharField(blank=True, help_text='Si vous le connaissez', max_length=15, verbose_name='Numéro de licence')),
                ('photo', models.FileField(blank=True, help_text='Si vous le pouvez, ajoutez la photo (formats JPEG). ', upload_to='certificats', verbose_name="Photo d'identité")),
                ('photo_valide', models.NullBooleanField(verbose_name='Certificat valide')),
                ('contact_nom', models.CharField(help_text='Personne a contacter en cas de problème ou responsable légale pour un mineur', max_length=200, verbose_name='Nom')),
                ('contact_telephone', models.CharField(max_length=200, verbose_name='Téléphone')),
                ('contact_email', models.EmailField(blank=True, max_length=200, verbose_name='e-mail')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name="Date d'insciption")),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Saison',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annee', models.IntegerField()),
                ('ouvert', models.BooleanField()),
            ],
        ),
        migrations.AddField(
            model_name='licence',
            name='membre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licences', to='members.Membre'),
        ),
        migrations.AddField(
            model_name='licence',
            name='saison',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membres', to='members.Saison'),
        ),
    ]
