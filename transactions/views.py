from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction
from categories.models import Category
from .forms import TransactionForm 
from django.db.models import Sum
import django_filters
from django.http import JsonResponse


class TransactionFilter(django_filters.FilterSet):
    class Meta:
        model = Transaction
        fields = {
            'title': ['icontains'],
            'amount': ['lt', 'gt'],
            'date': ['year', 'month', 'day'],
            'type': ['exact'],
            'category': ['exact'],
        }


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
    transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')

    # Initialize the filter with request data
    transaction_filter = TransactionFilter(request.GET, queryset=transactions)
    transactions = transaction_filter.qs

    # Calculate totals
    income_total = transactions.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = transactions.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income_total - expense_total

    context = {
        'transactions': transactions,
        'filter': transaction_filter,
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
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