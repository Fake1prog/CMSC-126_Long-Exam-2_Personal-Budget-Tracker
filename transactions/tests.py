import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from transactions.models import Transaction
from categories.models import Category
from datetime import date, timedelta
from decimal import Decimal
import time

@pytest.mark.django_db
class TestTransactionsFull:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='testpass')

    @pytest.fixture
    def other_user(self):
        return User.objects.create_user(username='otheruser', password='otherpass')

    @pytest.fixture
    def client_logged_in(self, client, user):
        client.login(username='testuser', password='testpass')
        return client

    @pytest.fixture
    def income_category(self, user):
        return Category.objects.create(user=user, name="Salary", type="INCOME", is_active=True)

    @pytest.fixture
    def expense_category(self, user):
        return Category.objects.create(user=user, name="Food", type="EXPENSE", is_active=True)

    @pytest.fixture
    def inactive_category(self, user):
        return Category.objects.create(user=user, name="Old", type="INCOME", is_active=False)

    def test_transaction_creation(self, client_logged_in, income_category, user):
        url = reverse("transaction_add")
        data = {
            "title": "Test Income",
            "amount": 5000.00,
            "date": date.today(),
            "type": "INCOME",
            "category": income_category.id,
            "notes": "Monthly salary",
        }
        response = client_logged_in.post(url, data)
        assert response.status_code == 302
        assert Transaction.objects.filter(user=user, title="Test Income").exists()

    def test_transaction_list_view(self, client_logged_in, user):
        Transaction.objects.create(
            title="Groceries",
            amount=150.00,
            date=date.today(),
            type="EXPENSE",
            user=user
        )
        url = reverse("transaction_list")
        response = client_logged_in.get(url)
        assert response.status_code == 200
        assert "Groceries" in response.content.decode()

    def test_transaction_edit(self, client_logged_in, user, income_category):
        transaction = Transaction.objects.create(
            title="Old Title",
            amount=100,
            date=date.today(),
            type="INCOME",
            user=user,
            category=income_category
        )
        url = reverse("transaction_edit", args=[transaction.id])
        data = {
            "title": "Updated Title",
            "amount": 200,
            "date": date.today(),
            "type": "INCOME",
            "category": income_category.id,
            "notes": "",
        }
        response = client_logged_in.post(url, data)
        assert response.status_code == 302
        transaction.refresh_from_db()
        assert transaction.title == "Updated Title"
        assert transaction.amount == Decimal("200")

    def test_transaction_delete(self, client_logged_in, user, income_category):
        transaction = Transaction.objects.create(
            title="To Delete",
            amount=100,
            date=date.today(),
            type="EXPENSE",
            user=user,
            category=income_category
        )
        url = reverse("transaction_delete", args=[transaction.id])
        response = client_logged_in.post(url)
        assert response.status_code == 302
        assert not Transaction.objects.filter(id=transaction.id).exists()

    def test_transaction_access_control(self, client, user):
        other_user = User.objects.create_user(username='otheruser', password='pass')
        transaction = Transaction.objects.create(
            title="Hidden",
            amount=100,
            date=date.today(),
            type="INCOME",
            user=other_user
        )
        client.login(username='testuser', password='testpass')
        url = reverse("transaction_edit", args=[transaction.id])
        response = client.get(url)
        assert response.status_code == 404

    def test_transaction_form_invalid_missing_fields(self, client_logged_in):
        response = client_logged_in.post(reverse("transaction_add"), {})
        assert response.status_code == 200
        assert "This field is required" in response.content.decode()

    def test_invalid_amount_negative_value(self, client_logged_in, income_category):
        data = {
            "title": "Invalid",
            "amount": -50,
            "date": date.today(),
            "type": "INCOME",
            "category": income_category.id,
        }
        response = client_logged_in.post(reverse("transaction_add"), data)
        assert response.status_code == 200
        assert "Ensure this value is greater than or equal to 0.01" in response.content.decode()

    def test_category_type_mismatch_triggers_default(self, client_logged_in, user, expense_category):
        data = {
            "title": "Wrong Category Type",
            "amount": 100,
            "date": date.today(),
            "type": "INCOME",
            "category": expense_category.id,
            "notes": ""
        }
        response = client_logged_in.post(reverse("transaction_add"), data)
        assert response.status_code == 302
        transaction = Transaction.objects.get(title="Wrong Category Type")
        assert transaction.category.name == "Other"
        assert transaction.category.type == "INCOME"

    def test_transaction_filter_by_type(self, client_logged_in, user, income_category, expense_category):
        Transaction.objects.create(title="Income1", amount=1000, type="INCOME", user=user, date=date.today(), category=income_category)
        Transaction.objects.create(title="Expense1", amount=200, type="EXPENSE", user=user, date=date.today(), category=expense_category)

        response = client_logged_in.get(reverse("transaction_list"), {"type": "INCOME"})
        assert "Income1" in response.content.decode()
        assert "Expense1" not in response.content.decode()

    def test_transaction_filter_by_amount_range(self, client_logged_in, user, income_category):
        Transaction.objects.create(title="Small", amount=50, type="INCOME", user=user, date=date.today(), category=income_category)
        Transaction.objects.create(title="Big", amount=5000, type="INCOME", user=user, date=date.today(), category=income_category)

        response = client_logged_in.get(reverse("transaction_list"), {"amount__gt": 100, "amount__lt": 10000})
        content = response.content.decode()
        assert "Big" in content
        assert "Small" not in content

    def test_transaction_filter_by_date_range(self, client_logged_in, user, income_category):
        today = date.today()
        yesterday = today - timedelta(days=1)
        Transaction.objects.create(title="Today", amount=100, date=today, type="INCOME", user=user, category=income_category)
        Transaction.objects.create(title="Yesterday", amount=100, date=yesterday, type="INCOME", user=user, category=income_category)

        response = client_logged_in.get(reverse("transaction_list"), {"date__gte": today, "date__lte": today})
        content = response.content.decode()
        assert "Today" in content
        assert "Yesterday" not in content

    def test_zero_amount_not_allowed(self, client_logged_in, income_category):
        response = client_logged_in.post(reverse("transaction_add"), {
            "title": "Zero",
            "amount": 0,
            "date": date.today(),
            "type": "INCOME",
            "category": income_category.id,
        })
        assert response.status_code == 200
        assert "Ensure this value is greater than or equal to 0.01" in response.content.decode()

    def test_display_uncategorized_transaction(self, client_logged_in, user):
        Transaction.objects.create(title="No Category", amount=10, type="INCOME", date=date.today(), user=user)
        response = client_logged_in.get(reverse("transaction_list"))
        assert "Uncategorized" in response.content.decode()

    def test_duplicate_transaction_allowed_by_default(self, client_logged_in, user, income_category):
        for _ in range(2):
            Transaction.objects.create(title="Repeat", amount=999, type="INCOME", user=user, date=date.today(), category=income_category)
        assert Transaction.objects.filter(title="Repeat").count() == 2
    
    def test_transaction_ordering_by_date_then_created(self, client_logged_in, user, income_category):
        t1 = Transaction.objects.create(title="Older", amount=100, date=date(2023, 1, 1), type="INCOME", user=user, category=income_category)
        time.sleep(0.01)
        t2 = Transaction.objects.create(title="Newer", amount=100, date=date(2023, 5, 1), type="INCOME", user=user, category=income_category)
        time.sleep(0.01)
        t3 = Transaction.objects.create(title="SameDateNew", amount=100, date=date(2023, 5, 1), type="INCOME", user=user, category=income_category)

        transactions = Transaction.objects.filter(user=user).order_by('-date', '-created_at')
        titles = list(transactions.values_list("title", flat=True))
        assert titles == ["SameDateNew", "Newer", "Older"]

    def test_transaction_unicode_str_method(self, user):
        transaction = Transaction.objects.create(
            title="Salary",
            amount=2000,
            date=date.today(),
            type="INCOME",
            user=user
        )
        assert str(transaction) == "Salary - 2000.00 (Income)"

    def test_transaction_filter_combined(self, client_logged_in, user, income_category):
        Transaction.objects.create(title="A", amount=200, date=date.today(), type="INCOME", user=user, category=income_category)
        Transaction.objects.create(title="B", amount=100, date=date.today(), type="INCOME", user=user, category=income_category)
        
        # Simulate manual filtering
        filtered = Transaction.objects.filter(user=user, amount__gt=150, type="INCOME")
        titles = list(filtered.values_list("title", flat=True))
        assert "A" in titles
        assert "B" not in titles



    def test_transaction_date_range_with_js_flatpickr_params(self, client_logged_in, user, income_category):
        Transaction.objects.create(title="InRange", amount=100, date=date(2023, 5, 10), type="INCOME", user=user, category=income_category)
        Transaction.objects.create(title="OutRange", amount=100, date=date(2023, 4, 10), type="INCOME", user=user, category=income_category)
        response = client_logged_in.get(reverse("transaction_list"), {
            "date_start": "2023-05-01",
            "date_end": "2023-05-31",
            "date__gte": "2023-05-01",
            "date__lte": "2023-05-31"
        })
        content = response.content.decode()
        assert "InRange" in content
        assert "OutRange" not in content

    def test_notes_field_optional(self, client_logged_in, income_category, user):
        response = client_logged_in.post(reverse("transaction_add"), {
            "title": "No Notes",
            "amount": 500,
            "date": date.today(),
            "type": "INCOME",
            "category": income_category.id
        })
        assert response.status_code == 302
        transaction = Transaction.objects.get(title="No Notes")
        assert transaction.notes == ""

    def test_transaction_category_color_displayed(self, client_logged_in, user):
        category = Category.objects.create(user=user, name="Colored", type="EXPENSE", color="#123456")
        Transaction.objects.create(title="ColoredTx", amount=50, date=date.today(), type="EXPENSE", user=user, category=category)
        response = client_logged_in.get(reverse("transaction_list"))
        assert "#123456" in response.content.decode()

    def test_bulk_transaction_creation_performance(self, user, income_category, django_assert_num_queries):
        """Ensure bulk inserts don't trigger N+1 problems."""
        transactions = [
            Transaction(title=f"Tx {i}", amount=100, date=date.today(), type="INCOME", user=user, category=income_category)
            for i in range(100)
        ]
        with django_assert_num_queries(1):  # One for insert, one for category FK fetch
            Transaction.objects.bulk_create(transactions)
        assert Transaction.objects.filter(user=user).count() >= 100

    def test_transaction_with_unicode_and_special_characters(self, client_logged_in, income_category, user):
        unicode_title = "🎉 Über ✨ Rent 💸"
        response = client_logged_in.post(reverse("transaction_add"), {
            "title": unicode_title,
            "amount": 999,
            "date": date.today(),
            "type": "INCOME",
            "category": income_category.id,
        })
        assert response.status_code == 302
        assert Transaction.objects.filter(title=unicode_title).exists()

    def test_malformed_form_input_rejected(self, client_logged_in, income_category):
        # Amount as string
        response = client_logged_in.post(reverse("transaction_add"), {
            "title": "Invalid Amount",
            "amount": "one hundred",
            "date": date.today(),
            "type": "INCOME",
            "category": income_category.id,
        })
        assert response.status_code == 200
        assert "Enter a number." in response.content.decode()

    def test_duplicate_titles_are_allowed(self, client_logged_in, user, income_category):
        for _ in range(3):
            Transaction.objects.create(title="Same Title", amount=123, type="INCOME", user=user, date=date.today(), category=income_category)
        assert Transaction.objects.filter(title="Same Title", user=user).count() == 3

    def test_transaction_list_empty_state_html(self, client_logged_in):
        response = client_logged_in.get(reverse("transaction_list"))
        content = response.content.decode()
        assert "No transactions yet" in content or "Start adding income and expenses" in content

    def test_transaction_handles_deleted_category_gracefully(self, client_logged_in, user, income_category):
        tx = Transaction.objects.create(
            title="Temp Cat",
            amount=100,
            date=date.today(),
            type="INCOME",
            user=user,
            category=income_category
        )
        income_category.delete()
        response = client_logged_in.get(reverse("transaction_list"))
        assert "Uncategorized" in response.content.decode()
        tx.refresh_from_db()
        assert tx.category is None
