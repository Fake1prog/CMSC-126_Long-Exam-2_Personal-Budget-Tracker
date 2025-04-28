from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction
from categories.models import Category
from .forms import TransactionForm
from django.db.models import Sum
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


@login_required
def get_categories(request):
    """Return filtered categories as JSON based on transaction type."""
    transaction_type = request.GET.get('type')

    if transaction_type in ['INCOME', 'EXPENSE']:
        categories = Category.objects.filter(
            user=request.user,
            type=transaction_type,
            is_active=True
        ).values('id', 'name', 'color', 'icon')

        return JsonResponse({'categories': list(categories)})

    return JsonResponse({'categories': []})


@login_required
def transaction_list(request):
    """Display a list of user's transactions with filtering."""
    # Start with all user transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')

    # Get distinct categories for the user
    categories = Category.objects.filter(user=request.user, is_active=True).distinct()

    # Debug information - log all request parameters
    if request.GET:
        logger.debug(f"Filter parameters: {request.GET}")

    # Manually apply filters for reliable behavior
    filter_applied = False

    # Title filter (case insensitive contains)
    if title_query := request.GET.get('title__icontains', '').strip():
        filter_applied = True
        logger.debug(f"Filtering by title: {title_query}")
        transactions = transactions.filter(title__icontains=title_query)

    # Amount filters
    if min_amount := request.GET.get('amount__gt', '').strip():
        try:
            min_amount_float = float(min_amount)
            filter_applied = True
            logger.debug(f"Filtering by min amount: {min_amount_float}")
            transactions = transactions.filter(amount__gt=min_amount_float)
        except (ValueError, TypeError):
            logger.warning(f"Invalid min amount: {min_amount}")

    if max_amount := request.GET.get('amount__lt', '').strip():
        try:
            max_amount_float = float(max_amount)
            filter_applied = True
            logger.debug(f"Filtering by max amount: {max_amount_float}")
            transactions = transactions.filter(amount__lt=max_amount_float)
        except (ValueError, TypeError):
            logger.warning(f"Invalid max amount: {max_amount}")

    # Date filters
    if start_date := request.GET.get('date__gte', '').strip():
        filter_applied = True
        logger.debug(f"Filtering by start date: {start_date}")
        transactions = transactions.filter(date__gte=start_date)

    if end_date := request.GET.get('date__lte', '').strip():
        filter_applied = True
        logger.debug(f"Filtering by end date: {end_date}")
        transactions = transactions.filter(date__lte=end_date)

    # Type filter (INCOME or EXPENSE)
    if transaction_type := request.GET.get('type', '').strip():
        if transaction_type in ['INCOME', 'EXPENSE']:
            filter_applied = True
            logger.debug(f"Filtering by type: {transaction_type}")
            transactions = transactions.filter(type=transaction_type)

    # Category filter
    if category_id := request.GET.get('category', '').strip():
        if category_id and category_id.isdigit():
            filter_applied = True
            logger.debug(f"Filtering by category ID: {category_id}")
            transactions = transactions.filter(category_id=category_id)

    # Log results
    if filter_applied:
        logger.debug(f"Filter applied, found {transactions.count()} transactions")

    # Calculate totals for the filtered results
    income_total = transactions.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = transactions.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income_total - expense_total

    context = {
        'transactions': transactions,
        'categories': categories,
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'filter_params': request.GET,  # Pass filter params for form repopulation
    }
    return render(request, 'transactions/transaction_list.html', context)


@login_required
def transaction_add(request):
    """Add a new transaction."""
    # Pre-set the type if provided in GET parameters
    initial_type = None
    if request.GET.get('type') in ['INCOME', 'EXPENSE']:
        initial_type = request.GET.get('type')

    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user, initial_type=initial_type)

    context = {
        'form': form,
        'title': 'Add Transaction',
    }
    return render(request, 'transactions/transaction_form.html', context)


@login_required
def transaction_edit(request, transaction_id):
    """Edit an existing transaction."""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(
            instance=transaction,
            user=request.user,
            initial_type=transaction.type
        )

    context = {
        'form': form,
        'title': 'Edit Transaction',
    }
    return render(request, 'transactions/transaction_form.html', context)


@login_required
def transaction_delete(request, transaction_id):
    """Delete a transaction."""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')

    context = {
        'object': transaction,
        'title': 'Delete Transaction',
    }
    return render(request, 'transactions/transaction_confirm_delete.html', context)