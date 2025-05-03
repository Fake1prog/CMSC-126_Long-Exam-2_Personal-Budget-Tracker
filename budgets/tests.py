import pytest
from django.contrib.auth.models import User
from categories.models import Category
from transactions.models import Transaction
from budgets.models import Budget
from datetime import date, timedelta
from decimal import Decimal


@pytest.mark.django_db
class TestBudgetModel:

    @pytest.fixture
    def setup_data(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        category = Category.objects.create(name='Food', type='EXPENSE', user=user, is_active=True)
        budget = Budget.objects.create(
            category=category,
            amount=Decimal('1000.00'),
            period='MONTHLY',
            start_date=date.today() - timedelta(days=15),
            end_date=date.today() + timedelta(days=15),
            user=user
        )
        return user, category, budget

    def test_budget_creation(self, setup_data):
        _, _, budget = setup_data
        assert str(budget) == f"{budget.category.name} Budget: {budget.amount} (Monthly)"

    def test_spent_no_transactions(self, setup_data):
        _, _, budget = setup_data
        assert budget.calculate_spent() == 0

    def test_spent_ignores_income_transactions(self, setup_data):
        user, category, budget = setup_data
        Transaction.objects.create(
            title='Salary',
            amount=Decimal('500.00'),
            category=category,
            user=user,
            type='INCOME',
            date=date.today()
        )
        assert budget.calculate_spent() == 0

    def test_spent_ignores_future_transactions(self, setup_data):
        user, category, budget = setup_data
        Transaction.objects.create(
            title='Future Expense',
            amount=Decimal('100.00'),
            category=category,
            user=user,
            type='EXPENSE',
            date=date.today() + timedelta(days=10)
        )
        assert budget.calculate_spent(end_date=date.today()) == 0

    def test_remaining_with_null_end_date(self):
        user = User.objects.create_user(username='user2', password='pass')
        category = Category.objects.create(name='Utilities', type='EXPENSE', user=user, is_active=True)
        budget = Budget.objects.create(
            category=category,
            amount=Decimal('600.00'),
            period='MONTHLY',
            start_date=date.today() - timedelta(days=10),
            end_date=None,
            user=user
        )
        Transaction.objects.create(
            title='Electric Bill',
            amount=Decimal('250.00'),
            category=category,
            user=user,
            type='EXPENSE',
            date=date.today()
        )
        assert budget.calculate_remaining() == Decimal('350.00')

    def test_multiple_transactions_aggregation(self, setup_data):
        user, category, budget = setup_data
        Transaction.objects.bulk_create([
            Transaction(title='Food1', amount=Decimal('100.00'), category=category, user=user, type='EXPENSE', date=date.today()),
            Transaction(title='Food2', amount=Decimal('300.00'), category=category, user=user, type='EXPENSE', date=date.today())
        ])
        assert budget.calculate_spent() == Decimal('400.00')
        assert budget.calculate_remaining() == Decimal('600.00')
        assert budget.is_over_budget() is False

    def test_budget_zero_amount_not_allowed(self, setup_data):
        user, category, _ = setup_data
        budget = Budget(
            category=category,
            amount=Decimal('0.00'),
            period='MONTHLY',
            start_date=date.today(),
            user=user
        )
        with pytest.raises(Exception):
            budget.full_clean()  # Validate field constraints

    def test_negative_amount_not_allowed(self, setup_data):
        user, category, _ = setup_data
        budget = Budget(
            category=category,
            amount=Decimal('-100.00'),
            period='MONTHLY',
            start_date=date.today(),
            user=user
        )
        with pytest.raises(Exception):
            budget.full_clean()  # Validate field constraints

    def test_spent_transaction_on_start_date(self, setup_data):
        user, category, budget = setup_data
        Transaction.objects.create(
            title='Opening Day Expense',
            amount=Decimal('100.00'),
            category=category,
            user=user,
            type='EXPENSE',
            date=budget.start_date
        )
        assert budget.calculate_spent() == Decimal('100.00')

    def test_spent_transaction_on_end_date(self, setup_data):
        user, category, budget = setup_data
        Transaction.objects.create(
            title='Final Day Expense',
            amount=Decimal('100.00'),
            category=category,
            user=user,
            type='EXPENSE',
            date=budget.end_date
        )
        assert budget.calculate_spent(end_date=budget.end_date) == Decimal('100.00')

    def test_transaction_with_different_user_not_counted(self, setup_data):
        _, category, budget = setup_data
        other_user = User.objects.create_user(username='otheruser', password='pass')
        Transaction.objects.create(
            title='Wrong User Expense',
            amount=Decimal('999.00'),
            category=category,
            user=other_user,
            type='EXPENSE',
            date=date.today()
        )
        assert budget.calculate_spent() == 0

    def test_transaction_with_different_category_not_counted(self, setup_data):
        user, _, budget = setup_data
        other_category = Category.objects.create(name='Travel', type='EXPENSE', user=user, is_active=True)
        Transaction.objects.create(
            title='Unrelated Expense',
            amount=Decimal('500.00'),
            category=other_category,
            user=user,
            type='EXPENSE',
            date=date.today()
        )
        assert budget.calculate_spent() == 0

    def test_transaction_outside_budget_range(self, setup_data):
        user, category, budget = setup_data
        out_of_range_date = budget.start_date - timedelta(days=5)
        Transaction.objects.create(
            title='Too Early Expense',
            amount=Decimal('300.00'),
            category=category,
            user=user,
            type='EXPENSE',
            date=out_of_range_date
        )
        assert budget.calculate_spent() == 0
