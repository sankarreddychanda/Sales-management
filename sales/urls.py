from django.urls import path
from .views import admin_dashboard, sales_dashboard
from .views import sales_dashboard, enroll_student, record_payment, view_pending_payments,sales_home ,create_pending_payment

urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('', sales_dashboard, name='sales_dashboard'),
    path('create-pending-payment/<int:student_id>/', create_pending_payment, name='create_pending_payment'),

    path('', sales_home, name='sales_home'),
    path('enroll-student/', enroll_student, name='enroll_student'),
    path('record-payment/<int:student_id>/', record_payment, name='record_payment'),
    path('pending-payments/', view_pending_payments, name='view_pending_payments'),
]
