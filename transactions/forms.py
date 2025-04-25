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
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Default to today's date for new transactions
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()

        # Filter categories by user
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user,
                is_active=True
            )