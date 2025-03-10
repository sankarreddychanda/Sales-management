from django.db import models
from django.conf import settings


# Salesperson Model (User model will act as Salesperson)
class SalesPerson(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Class Model
class TrainingClass(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


# Student Model
class Student(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    joined_date = models.DateField(auto_now_add=True)
    training_class = models.ForeignKey(TrainingClass, on_delete=models.CASCADE)
    salesperson = models.ForeignKey(SalesPerson, on_delete=models.SET_NULL, null=True, blank=True)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ Add this field

    def __str__(self):
        return self.name


# Payment Model
class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    collected_by = models.ForeignKey(SalesPerson, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.amount_paid}"

from django.utils.timezone import now
from django.db.models import Sum

# Pending Payment Model
class PendingPayment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Ensure `total_fee` is not None
        total_fee = self.student.total_fees if self.student.total_fees is not None else 0

        # Ensure `amount_paid` is not None
        amount_paid = Payment.objects.filter(student=self.student).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        # Calculate due amount
        self.due_amount = total_fee - amount_paid

        super().save(*args, **kwargs)


