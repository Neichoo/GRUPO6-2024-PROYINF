# Generated by Django 5.1.1 on 2025-06-16 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Interfaz', '0015_boletinborrador'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletinborrador',
            name='contenido_html',
            field=models.TextField(blank=True),
        ),
    ]
