from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum
from decimal import Decimal
import json

from .models import Student, Payment, PendingPayment, TrainingClass, SalesPerson


# Sales Home View
@login_required
def sales_home(request):
    return render(request, "sales/home.html")


# Admin Dashboard
from django.shortcuts import render
from django.db.models import Sum
from .models import Student, Payment, PendingPayment, SalesPerson
import json

@login_required
def admin_dashboard(request):
    # Ensure only admin users can access this view
    if not request.user.role == 'admin':
        return redirect('home')

    # Fetch data
    total_students = Student.objects.count()
    total_collected = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_pending = PendingPayment.objects.aggregate(Sum('due_amount'))['due_amount__sum'] or 0

    # Fetch salesperson data
    sales_data = SalesPerson.objects.annotate(total_collection=Sum('payment__amount_paid'))
    salespersons = [sales.user.get_full_name() or sales.user.username for sales in sales_data]
    collections = [float(sales.total_collection or 0) for sales in sales_data]

    context = {
        'total_students': total_students,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'sales_data': sales_data,
        'salespersons': json.dumps(salespersons),  # Convert to JSON for Chart.js
        'collections': json.dumps(collections),    # Convert to JSON for Chart.js
    }
    return render(request, 'admin_dashboard.html', context)
# Custom Login View
class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.role == "sales":
            return reverse("sales_dashboard")
        elif user.role == "admin":
            return reverse("admin_dashboard")
        return reverse("home")  # Fallback


# Salesperson Permission Decorator
def sales_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, "role", None) == "sales":
            return view_func(request, *args, **kwargs)
        return redirect("login")

    return wrapper


# Salesperson Dashboard
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import SalesPerson, Student, Payment, PendingPayment

@login_required
@sales_required
def sales_dashboard(request):
    try:
        # Try to get the SalesPerson object for the logged-in user
        salesperson = SalesPerson.objects.get(user=request.user)
    except SalesPerson.DoesNotExist:
        # If the SalesPerson object doesn't exist, create it
        salesperson = SalesPerson.objects.create(user=request.user)

    # Fetch data for the dashboard
    students = Student.objects.filter(salesperson=salesperson)
    total_collected = Payment.objects.filter(collected_by=salesperson).aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0
    pending_payments = PendingPayment.objects.filter(student__salesperson=salesperson, due_amount__gt=0)
    fully_paid_students = students.exclude(id__in=pending_payments.values_list("student_id", flat=True))

    context = {
        "students": students,
        "total_collected": total_collected,
        "pending_payments": pending_payments,
        "fully_paid_students": fully_paid_students,
    }
    return render(request, "sales_dashboard.html", context)

# Enroll a Student
@login_required
@sales_required
def enroll_student(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        training_class = get_object_or_404(TrainingClass, id=request.POST["training_class"])
        salesperson = get_object_or_404(SalesPerson, user=request.user)
        total_fees = request.POST["total_fees"]

        student = Student.objects.create(
            name=name,
            email=email,
            phone=phone,
            training_class=training_class,
            salesperson=salesperson,
            total_fees=total_fees,
        )
        messages.success(request, f"Student {name} enrolled successfully!")
        return redirect("sales_dashboard")

    classes = TrainingClass.objects.all()
    return render(request, "sales/enroll_student.html", {"classes": classes})


# Record Payment
@login_required
def record_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    salesperson = get_object_or_404(SalesPerson, user=request.user)
    pending_payment = PendingPayment.objects.filter(student=student).first()
    pending_amount = pending_payment.due_amount if pending_payment else Decimal("0.00")

    if request.method == "POST":
        amount_paid = Decimal(request.POST.get("amount_paid"))
        payment_status = request.POST.get("payment_status")  # 'full' or 'partial'

        # Save Payment
        Payment.objects.create(student=student, collected_by=salesperson, amount_paid=amount_paid)

        if payment_status == "full" or amount_paid >= pending_amount:
            PendingPayment.objects.filter(student=student).delete()
        else:
            if pending_payment:
                pending_payment.due_amount -= amount_paid
                pending_payment.delete() if pending_payment.due_amount <= 0 else pending_payment.save()

        return redirect("sales_dashboard")

    context = {
        "student": student,
        "pending_amount": pending_amount,
    }
    return render(request, "sales/record_payment.html", context)


# View Pending Payments
@login_required
@sales_required
def view_pending_payments(request):
    salesperson = get_object_or_404(SalesPerson, user=request.user)
    pending_payments = PendingPayment.objects.filter(student__salesperson=salesperson, due_amount__gt=0)
    return render(request, "sales/pending_payments.html", {"pending_payments": pending_payments})


# Create Pending Payment
@login_required
def create_pending_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    total_fees = student.total_fees if student.total_fees is not None else 0
    total_paid = Payment.objects.filter(student=student).aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0
    pending_amount = total_fees - total_paid

    if request.method == "POST":
        due_amount = float(request.POST.get("due_amount", 0))
        PendingPayment.objects.create(student=student, due_amount=due_amount)
        return redirect("sales_dashboard")

    return render(request, "sales/create_pending_payment.html", {"student": student, "pending_amount": pending_amount})
