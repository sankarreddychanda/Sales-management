from django.contrib import admin
from .models import SalesPerson, TrainingClass, Student, Payment, PendingPayment

admin.site.register(SalesPerson)
admin.site.register(TrainingClass)
admin.site.register(Student)
admin.site.register(Payment)
admin.site.register(PendingPayment)
