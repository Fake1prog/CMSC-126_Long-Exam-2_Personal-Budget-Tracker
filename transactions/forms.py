from django import forms
from .models import Transaction
from categories.models import Category
from django.utils import timezone


class DateInput(forms.DateInput):
    input_type = 'date'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'date', 'type', 'category', 'notes']
        widgets = {
            'date': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        transaction_type = kwargs.pop('initial_type', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Default to today's date for new transactions
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()

        # Filter categories by user
        if user:
            # Start with all user categories
            categories = Category.objects.filter(
                user=user,
                is_active=True
            )

            # If we know the transaction type (from URL parameter or instance)
            if transaction_type:
                self.fields['type'].initial = transaction_type
                categories = categories.filter(type=transaction_type)
            elif self.instance.pk and self.instance.type:
                # For existing transactions, filter by their type
                categories = categories.filter(type=self.instance.type)

            self.fields['category'].queryset = categories

            # Add class for JS filtering
            self.fields['type'].widget.attrs.update({'class': 'transaction-type-select'})
            self.fields['category'].widget.attrs.update({'class': 'category-select'})