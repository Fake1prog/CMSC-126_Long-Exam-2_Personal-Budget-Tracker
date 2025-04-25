from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Budget
from .forms import BudgetForm
from datetime import date


@login_required
def budget_list(request):
    """Display a list of user's budgets."""
    budgets = Budget.objects.filter(user=request.user)

    # Calculate current status for each budget
    for budget in budgets:
        budget.spent = budget.calculate_spent()
        budget.remaining = budget.calculate_remaining()
        budget.is_over = budget.is_over_budget()

    context = {
        'budgets': budgets,
    }
    return render(request, 'budgets/budget_list.html', context)


@login_required
def budget_add(request):
    """Add a new budget."""
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, f'Budget for {budget.category.name} created successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)

    context = {
        'form': form,
        'title': 'Add Budget',
    }
    return render(request, 'budgets/budget_form.html', context)


@login_required
def budget_edit(request, budget_id):
    """Edit an existing budget."""
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Budget for {budget.category.name} updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)

    context = {
        'form': form,
        'title': 'Edit Budget',
    }
    return render(request, 'budgets/budget_form.html', context)


@login_required
def budget_delete(request, budget_id):
    """Delete a budget."""
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, f'Budget for {budget.category.name} deleted successfully!')
        return redirect('budget_list')

    context = {
        'object': budget,
        'title': 'Delete Budget',
    }
    return render(request, 'budgets/budget_confirm_delete.html', context)