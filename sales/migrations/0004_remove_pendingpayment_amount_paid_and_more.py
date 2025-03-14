# Generated by Django 5.0.4 on 2025-03-10 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_student_total_fees'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pendingpayment',
            name='amount_paid',
        ),
        migrations.RemoveField(
            model_name='pendingpayment',
            name='due_date',
        ),
        migrations.RemoveField(
            model_name='pendingpayment',
            name='total_fee',
        ),
        migrations.AlterField(
            model_name='pendingpayment',
            name='due_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
