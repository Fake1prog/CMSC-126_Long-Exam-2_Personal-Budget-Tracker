from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from transactions.models import Transaction
from categories.models import Category
from django.db.models import Sum
from django.utils import timezone
import csv
from datetime import datetime, timedelta


@login_required
def report_dashboard(request):
    """Main reports dashboard."""
    # Get summary data for quick stats
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    # Current month stats
    current_month_income = Transaction.objects.filter(
        user=request.user,
        type='INCOME',
        date__gte=start_of_month,
        date__lte=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    current_month_expenses = Transaction.objects.filter(
        user=request.user,
        type='EXPENSE',
        date__gte=start_of_month,
        date__lte=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # All time stats
    total_income = Transaction.objects.filter(
        user=request.user,
        type='INCOME'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_expenses = Transaction.objects.filter(
        user=request.user,
        type='EXPENSE'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Get recent reports
    recent_months = []
    for i in range(3):
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        month_name = month_date.strftime("%B %Y")
        recent_months.append({
            'name': month_name,
            'month': month_date.month,
            'year': month_date.year
        })

    context = {
        'title': 'Reports',
        'current_month_income': current_month_income,
        'current_month_expenses': current_month_expenses,
        'current_month_balance': current_month_income - current_month_expenses,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_balance': total_income - total_expenses,
        'recent_months': recent_months,
        'has_transactions': Transaction.objects.filter(user=request.user).exists()
    }
    return render(request, 'reports/report_dashboard.html', context)


@login_required
def monthly_report(request):
    """Monthly income and expense report."""
    # Get all user transactions first to check if any exist
    has_any_transactions = Transaction.objects.filter(user=request.user).exists()

    # Get user's oldest transaction date for validation
    oldest_transaction = Transaction.objects.filter(user=request.user).order_by('date').first()

    # Get selected month or default to current month
    today = timezone.now().date()
    month = request.GET.get('month', today.month)
    year = request.GET.get('year', today.year)

    try:
        month = int(month)
        year = int(year)
        if month < 1 or month > 12:
            month = today.month
    except (ValueError, TypeError):
        month = today.month
        year = today.year

    # Create date range
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)

    # Get transactions for the month
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    # Calculate totals
    income_total = transactions.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = transactions.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0

    # Group by category
    income_by_category = transactions.filter(type='INCOME').values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')

    expense_by_category = transactions.filter(type='EXPENSE').values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Generate month navigation options
    month_options = []
    if oldest_transaction:
        oldest_date = oldest_transaction.date
        current_date = datetime(today.year, today.month, 1).date()

        while current_date >= oldest_date.replace(day=1):
            month_options.append({
                'month': current_date.month,
                'year': current_date.year,
                'name': current_date.strftime('%B %Y'),
                'selected': current_date.month == month and current_date.year == year
            })

            # Move to previous month
            if current_date.month == 1:
                current_date = datetime(current_date.year - 1, 12, 1).date()
            else:
                current_date = datetime(current_date.year, current_date.month - 1, 1).date()

    context = {
        'transactions': transactions,
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': income_total - expense_total,
        'income_by_category': income_by_category,
        'expense_by_category': expense_by_category,
        'start_date': start_date,
        'end_date': end_date,
        'month': month,
        'year': year,
        'month_options': month_options,
        'has_any_transactions': has_any_transactions,
        'oldest_transaction_date': oldest_transaction.date if oldest_transaction else None,
    }
    return render(request, 'reports/monthly_report.html', context)


@login_required
def category_report(request):
    """Category-based spending report."""
    # Check if user has any transactions
    has_any_transactions = Transaction.objects.filter(user=request.user).exists()

    # Get selected category or show all
    category_id = request.GET.get('category')
    if category_id:
        try:
            category = Category.objects.get(id=category_id, user=request.user)
        except Category.DoesNotExist:
            category = None
    else:
        category = None

    # Get date range or default to last 3 months
    today = timezone.now().date()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        start_date = today - timedelta(days=90)

    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        end_date = today

    # Filter transactions
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )

    if category:
        transactions = transactions.filter(category=category)

    # Calculate total income and expenses for the summary section
    total_income = transactions.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0

    # Group by date (monthly)
    monthly_data = {}
    for transaction in transactions:
        month_key = f"{transaction.date.year}-{transaction.date.month:02d}"
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'income': 0,
                'expense': 0
            }

        if transaction.type == 'INCOME':
            monthly_data[month_key]['income'] += transaction.amount
        else:
            monthly_data[month_key]['expense'] += transaction.amount

    # Convert to list for template
    monthly_data_list = [
        {
            'month': key,
            'income': value['income'],
            'expense': value['expense'],
            'balance': value['income'] - value['expense']
        }
        for key, value in sorted(monthly_data.items())
    ]

    context = {
        'categories': Category.objects.filter(user=request.user, is_active=True),
        'selected_category': category,
        'start_date': start_date,
        'end_date': end_date,
        'transactions': transactions,
        'monthly_data': monthly_data_list,
        'has_any_transactions': has_any_transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
    }
    return render(request, 'reports/category_report.html', context)


@login_required
def export_data(request):
    """Export transactions as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    # Get date range
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        start_date = timezone.now().date() - timedelta(days=365)  # Last year

    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        end_date = timezone.now().date()

    # Get transactions
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    # Create CSV writer
    writer = csv.writer(response)
    writer.writerow(['Date', 'Title', 'Type', 'Category', 'Amount', 'Notes'])

    for transaction in transactions:
        writer.writerow([
            transaction.date,
            transaction.title,
            transaction.get_type_display(),
            transaction.category.name if transaction.category else 'Uncategorized',
            transaction.amount,
            transaction.notes
        ])

    return response