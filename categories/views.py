from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category
from .forms import CategoryForm


@login_required
def category_list(request):
    """Display a list of user's categories."""
    income_categories = Category.objects.filter(user=request.user, type='INCOME', is_active=True)
    expense_categories = Category.objects.filter(user=request.user, type='EXPENSE', is_active=True)

    context = {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
    }
    return render(request, 'categories/category_list.html', context)


@login_required
def category_add(request):
    """Add a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'title': 'Add Category',
    }
    return render(request, 'categories/category_form.html', context)


@login_required
def category_edit(request, category_id):
    """Edit an existing category."""
    category = get_object_or_404(Category, id=category_id, user=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'title': 'Edit Category',
    }
    return render(request, 'categories/category_form.html', context)


@login_required
def category_delete(request, category_id):
    """Delete (or archive) a category."""
    category = get_object_or_404(Category, id=category_id, user=request.user)

    if request.method == 'POST':
        # Use soft delete method from the model
        result = category.soft_delete()
        if result:
            messages.success(request, f'Category "{category.name}" deleted successfully!')
        else:
            messages.error(request, 'An error occurred while deleting the category.')
        return redirect('category_list')

    context = {
        'object': category,
        'title': 'Delete Category',
    }
    return render(request, 'categories/category_confirm_delete.html', context)