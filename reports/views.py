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
    context = {
        'title': 'Reports',
    }
    return render(request, 'reports/report_dashboard.html', context)


@login_required
def monthly_report(request):
    """Monthly income and expense report."""
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
    income_by_category = transactions.filter(type='INCOME').values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')

    expense_by_category = transactions.filter(type='EXPENSE').values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')

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
    }
    return render(request, 'reports/monthly_report.html', context)


@login_required
def category_report(request):
    """Category-based spending report."""
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