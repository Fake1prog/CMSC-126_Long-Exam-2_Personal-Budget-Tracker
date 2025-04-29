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


def about(request):
    """About page view."""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page view."""
    return render(request, 'core/contact.html')


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
        type='EXPENSE'
    ).values(
        'category',  # Group by category ID first
        'category__name',
        'category__color'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Handle null categories properly
    for category in expense_by_category:
        if category['category__name'] is None:
            category['category__name'] = 'Uncategorized'
        if category['category__color'] is None:
            category['category__color'] = '#808080'

    # Print debug info
    print(f"Found {len(expense_by_category)} expense categories")
    for category in expense_by_category:
        print(f"Category: {category['category__name']}, Amount: {category['total']}")

    # Get individual expense transactions (all time)
    expense_transactions = Transaction.objects.filter(
        user=request.user,
        type='EXPENSE'
    ).order_by('-amount')

    # Format transaction data for the chart
    expense_by_transaction = []
    for transaction in expense_transactions:
        # Get the category color or use a default
        color = '#808080'
        category_name = 'Uncategorized'
        if transaction.category:
            color = transaction.category.color
            category_name = transaction.category.name

        expense_by_transaction.append({
            'title': transaction.title,
            'amount': float(transaction.amount),
            'color': color,
            'date': transaction.date.strftime('%Y-%m-%d'),
            'category': category_name
        })

    context = {
        'title': 'Dashboard',
        'income': income,
        'expenses': expenses,
        'balance': income - expenses,
        'recent_transactions': recent_transactions,
        'expense_by_category': expense_by_category,
        'expense_by_transaction': expense_by_transaction,
    }
    return render(request, 'core/dashboard.html', context)