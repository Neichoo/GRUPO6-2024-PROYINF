# Generated by Django 5.1.1 on 2024-11-06 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Interfaz', '0009_fuentesinfo_descripcion_fuentesinfo_estado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuentesinfo',
            name='descripcion',
            field=models.CharField(blank=True, default='', max_length=500, null=True),
        ),
    ]
