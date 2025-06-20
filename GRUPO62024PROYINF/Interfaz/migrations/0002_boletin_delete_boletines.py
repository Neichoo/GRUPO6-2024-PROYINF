# Generated by Django 5.1.1 on 2024-10-10 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Interfaz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boletin',
            fields=[
                ('id_boletin', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_boletin', models.CharField(max_length=100)),
                ('fecha_boletin', models.DateField()),
                ('tags_boletin', models.ManyToManyField(to='Interfaz.tag')),
            ],
        ),
        migrations.DeleteModel(
            name='Boletines',
        ),
    ]
