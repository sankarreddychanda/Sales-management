from django.shortcuts import render
from decimal import Decimal
# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def sales_home(request):
    return render(request, 'sales/home.html')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return render(request, '403.html')  # Unauthorized access
    return render(request, 'admin_dashboard.html')

# @login_required
# def sales_dashboard(request):
#     if request.user.role != 'sales':
#         return render(request, '403.html')  # Unauthorized access
#     return render(request, 'sales_dashboard.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, Payment, PendingPayment, TrainingClass, SalesPerson
from django.db.models import Sum


# Ensure only salespersons can access
def sales_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'sales':
            return view_func(request, *args, **kwargs)
        return redirect('login')

    return wrapper


# Salesperson Dashboard
@login_required
@sales_required
def sales_dashboard(request):
    salesperson = get_object_or_404(SalesPerson, user=request.user)

    # Get all students assigned to this salesperson
    students = Student.objects.filter(salesperson=salesperson)

    # Calculate the total amount collected by the salesperson
    total_collected = Payment.objects.filter(collected_by=salesperson).aggregate(Sum("amount_paid"))[
        "amount_paid__sum"] or 0

    # Get all pending payments where the due amount is greater than zero
    pending_payments = PendingPayment.objects.filter(student__salesperson=salesperson, due_amount__gt=0)

    # Ensure that only students with NO pending payments are marked as fully paid
    fully_paid_students = students.exclude(id__in=pending_payments.values_list("student_id", flat=True))

    context = {
        "students": students,
        "total_collected": total_collected,
        "pending_payments": pending_payments,
        "fully_paid_students": fully_paid_students
    }
    return render(request, "sales_dashboard.html", context)
# Enroll a Student
@login_required
@sales_required
def enroll_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        training_class = get_object_or_404(TrainingClass, id=request.POST['training_class'])
        salesperson = get_object_or_404(SalesPerson, user=request.user)

        student = Student.objects.create(
            name=name, email=email, phone=phone,
            training_class=training_class, salesperson=salesperson
        )
        messages.success(request, f"Student {name} enrolled successfully!")
        return redirect('sales_dashboard')

    classes = TrainingClass.objects.all()
    return render(request, 'sales/enroll_student.html', {'classes': classes})


@login_required
def record_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    salesperson = get_object_or_404(SalesPerson, user=request.user)

    # Get pending payment (if any)
    pending_payment = PendingPayment.objects.filter(student=student).first()
    pending_amount = pending_payment.due_amount if pending_payment else Decimal("0.00")

    if request.method == "POST":
        amount_paid = Decimal(request.POST.get("amount_paid"))  # Convert to Decimal for accuracy
        payment_status = request.POST.get("payment_status")  # 'full' or 'partial'

        # Record the payment
        Payment.objects.create(student=student, collected_by=salesperson, amount_paid=amount_paid)

        if payment_status == "full" or amount_paid >= pending_amount:
            # Full payment received, delete pending payment if exists
            PendingPayment.objects.filter(student=student).delete()
        else:
            # Partial payment, update pending amount
            if pending_payment:
                pending_payment.due_amount -= amount_paid
                if pending_payment.due_amount <= 0:
                    pending_payment.delete()
                else:
                    pending_payment.save()

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

    return render(request, 'sales/pending_payments.html', {'pending_payments': pending_payments})
@login_required
def create_pending_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Ensure total_fees is not None
    total_fees = student.total_fees if student.total_fees is not None else 0

    # Ensure total_paid is not None
    total_paid = Payment.objects.filter(student=student).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    # Calculate pending amount
    pending_amount = total_fees - total_paid

    # Save pending amount when the form is submitted
    if request.method == 'POST':
        due_amount = request.POST.get('due_amount', 0)

        # Ensure due_amount is a valid number
        due_amount = float(due_amount) if due_amount else 0

        PendingPayment.objects.create(student=student, due_amount=due_amount)
        return redirect('sales_dashboard')  # Redirect after saving

    return render(request, 'sales/create_pending_payment.html', {'student': student, 'pending_amount': pending_amount})