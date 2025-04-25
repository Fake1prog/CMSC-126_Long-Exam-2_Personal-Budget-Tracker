from django import forms
from .models import Budget
from categories.models import Category


class DateInput(forms.DateInput):
    input_type = 'date'


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'period', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(BudgetForm, self).__init__(*args, **kwargs)

        # Filter categories by user and type (only expense categories)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user,
                type='EXPENSE',
                is_active=True
            )