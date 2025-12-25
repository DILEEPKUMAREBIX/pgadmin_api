from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0020_rename_table_prefix'),
    ]

    operations = [
        migrations.AddField(
            model_name='resident',
            name='arrears',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
        ),
    ]
