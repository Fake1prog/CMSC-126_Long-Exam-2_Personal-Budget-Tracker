from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction
from categories.models import Category
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta


def home(request):
    """Home page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    """Dashboard view for authenticated users."""
    # Get current month data
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    # Get income and expenses for current month
    income = Transaction.objects.filter(
        user=request.user,
        type='INCOME',
        date__gte=start_of_month,
        date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    expenses = Transaction.objects.filter(
        user=request.user,
        type='EXPENSE',
        date__gte=start_of_month,
        date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date')[:5]

    # Get expense breakdown by category
    expense_by_category = Transaction.objects.filter(
        user=request.user,
        type='EXPENSE',
        date__gte=start_of_month,
        date__lte=today
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')

    context = {
        'title': 'Dashboard',
        'income': income,
        'expenses': expenses,
        'balance': income - expenses,
        'recent_transactions': recent_transactions,
        'expense_by_category': expense_by_category,
    }
    return render(request, 'core/dashboard.html', context)