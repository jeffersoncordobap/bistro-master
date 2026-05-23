from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiqueteras', '0003_alter_consumotiquetera_comanda'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiquetera',
            name='codigo',
            field=models.CharField(max_length=30, unique=True, null=True, blank=True, help_text='Código único de la tiquetera (opcional).'),
        ),
    ]
