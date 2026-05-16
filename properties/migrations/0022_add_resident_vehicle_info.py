from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0021_add_resident_arrears'),
    ]

    operations = [
        migrations.AddField(
            model_name='resident',
            name='vehicle_2wheeler',
            field=models.CharField(
                blank=True,
                help_text='2 Wheeler vehicle registration number',
                max_length=50,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='resident',
            name='vehicle_4wheeler',
            field=models.CharField(
                blank=True,
                help_text='4 Wheeler vehicle registration number',
                max_length=50,
                null=True
            ),
        ),
    ]
