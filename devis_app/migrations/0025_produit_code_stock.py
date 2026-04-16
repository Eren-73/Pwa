from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devis_app', '0024_responsablecommercial'),
    ]

    operations = [
        migrations.AddField(
            model_name='produit',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='produit',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
