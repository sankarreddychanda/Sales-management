# Generated by Django 5.0.4 on 2025-03-10 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_alter_pendingpayment_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='total_fees',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
