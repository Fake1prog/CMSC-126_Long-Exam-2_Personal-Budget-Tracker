import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from categories.models import Category
from categories.forms import CategoryForm
from categories.templatetags.category_tags import as_category_options
from django.utils.html import escape

# ---------- Fixtures ----------
@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")

@pytest.fixture
def client_logged_in(client, user):
    client.login(username="testuser", password="testpass")
    return client

@pytest.fixture
def sample_category(user):
    return Category.objects.create(
        name="Test Category",
        type="EXPENSE",
        color="#FF5733",
        icon="🧾",
        user=user,
    )

# ---------- Model Tests ----------
def test_category_str(sample_category):
    assert str(sample_category) == "Test Category (Expense)"

def test_get_html_attributes(sample_category):
    attrs = sample_category.get_html_attributes()
    assert 'data-type="EXPENSE"' in attrs
    assert 'data-color="#FF5733"' in attrs
    assert 'data-icon="🧾"' in attrs

def test_category_soft_delete_no_transactions(sample_category):
    assert sample_category.soft_delete() is True
    assert not Category.objects.filter(id=sample_category.id).exists()

def test_soft_delete_with_real_transaction(sample_category, db):
    from transactions.models import Transaction

    Transaction.objects.create(
        category=sample_category,
        amount=100.0,
        type="EXPENSE",
        date="2024-01-01",
        user=sample_category.user
    )

    result = sample_category.soft_delete()
    sample_category.refresh_from_db()

    assert result is True
    assert sample_category.name.startswith("[Archived]")
    assert sample_category.is_active is False


# ---------- Form Tests ----------
def test_category_form_valid(user):
    form_data = {
        "name": "Valid Category",
        "type": "INCOME",
        "color": "#00FF00",
        "icon": "💰",
    }
    form = CategoryForm(data=form_data)
    assert form.is_valid()

def test_category_form_invalid_missing_name():
    form_data = {
        "type": "EXPENSE",
        "color": "#FF0000",
        "icon": "🚫",
    }
    form = CategoryForm(data=form_data)
    assert not form.is_valid()
    assert "name" in form.errors

def test_duplicate_category_name_same_user(client_logged_in, user):
    Category.objects.create(name="Duplicate", type="INCOME", color="#000000", icon="🔁", user=user)
    form_data = {
        "name": "Duplicate",
        "type": "EXPENSE",
        "color": "#FFFFFF",
        "icon": "🆗",
    }
    form = CategoryForm(data=form_data)
    assert form.is_valid()

def test_invalid_category_type_fails_validation():
    form_data = {
        "name": "Invalid Type",
        "type": "WRONGTYPE",
        "color": "#ABCDEF",
        "icon": "❓",
    }
    form = CategoryForm(data=form_data)
    assert not form.is_valid()
    assert "type" in form.errors

def test_category_form_widgets():
    form = CategoryForm()
    assert 'type="color"' in str(form['color'])
    assert 'form-control' in str(form['icon'])

# ---------- View Tests ----------
def test_redirect_if_not_logged_in(client):
    response = client.get(reverse("category_list"))
    assert response.status_code == 302
    assert "/login" in response.url

def test_category_list_view(client_logged_in):
    response = client_logged_in.get(reverse("category_list"))
    assert response.status_code == 200
    assert "Categories" in response.content.decode()

def test_category_add_view_get(client_logged_in):
    response = client_logged_in.get(reverse("category_add"))
    assert response.status_code == 200
    assert "Category" in response.content.decode()

def test_category_add_view_post(client_logged_in):
    data = {
        "name": "New Category",
        "type": "INCOME",
        "color": "#123456",
        "icon": "🆕"
    }
    response = client_logged_in.post(reverse("category_add"), data)
    assert response.status_code == 302
    assert Category.objects.filter(name="New Category").exists()

def test_category_add_invalid_post(client_logged_in):
    data = {
        "name": "",
        "type": "EXPENSE",
        "color": "#FF0000",
        "icon": "⚠️"
    }
    response = client_logged_in.post(reverse("category_add"), data)
    assert response.status_code == 200
    assert "This field is required" in response.content.decode()

def test_category_edit_view_post(client_logged_in, sample_category):
    url = reverse("category_edit", args=[sample_category.id])
    data = {
        "name": "Updated Category",
        "type": "EXPENSE",
        "color": "#654321",
        "icon": "🔄"
    }
    response = client_logged_in.post(url, data)
    assert response.status_code == 302
    sample_category.refresh_from_db()
    assert sample_category.name == "Updated Category"

def test_category_edit_invalid_post(client_logged_in, sample_category):
    url = reverse("category_edit", args=[sample_category.id])
    data = {
        "name": "",
        "type": "EXPENSE",
        "color": "#AAAAAA",
        "icon": "❌"
    }
    response = client_logged_in.post(url, data)
    assert response.status_code == 200
    assert "This field is required" in response.content.decode()

def test_category_delete_view_get(client_logged_in, sample_category):
    url = reverse("category_delete", args=[sample_category.id])
    response = client_logged_in.get(url)
    assert response.status_code == 200
    assert "Delete" in response.content.decode()

def test_category_delete_view_post(client_logged_in, sample_category):
    url = reverse("category_delete", args=[sample_category.id])
    response = client_logged_in.post(url)
    assert response.status_code == 302
    assert not Category.objects.filter(id=sample_category.id).exists()

def test_edit_category_forbidden(client, user):
    other_user = User.objects.create_user(username="intruder", password="badpass")
    cat = Category.objects.create(name="Private", type="EXPENSE", color="#111111", icon="🔒", user=user)

    client.login(username="intruder", password="badpass")
    response = client.get(reverse("category_edit", args=[cat.id]))
    assert response.status_code == 404

def test_delete_category_forbidden(client, user):
    other_user = User.objects.create_user(username="intruder", password="badpass")
    cat = Category.objects.create(name="PrivateDelete", type="EXPENSE", color="#222222", icon="🚫", user=user)

    client.login(username="intruder", password="badpass")
    response = client.post(reverse("category_delete", args=[cat.id]))
    assert response.status_code == 404

def test_archived_category_not_listed(client_logged_in, user):
    Category.objects.create(name="Visible", type="INCOME", color="#123123", icon="👀", user=user)
    Category.objects.create(name="Hidden", type="INCOME", color="#000000", icon="🙈", user=user, is_active=False)

    response = client_logged_in.get(reverse("category_list"))
    content = response.content.decode()
    assert "Visible" in content
    assert "Hidden" not in content

def test_category_list_filters_correct_types(client_logged_in, user):
    Category.objects.create(name="Salary", type="INCOME", color="#00FF00", icon="💰", user=user)
    Category.objects.create(name="Food", type="EXPENSE", color="#FF0000", icon="🍔", user=user)

    response = client_logged_in.get(reverse("category_list"))
    content = response.content.decode()
    assert "Salary" in content
    assert "Food" in content
    assert "💰" in content
    assert "🍔" in content

# ---------- Template Tag Tests ----------
def test_as_category_options_renders_expected_html(user):
    cat1 = Category.objects.create(name="Salary", type="INCOME", color="#00FF00", icon="💰", user=user)
    cat2 = Category.objects.create(name="Gift", type="INCOME", color="#FF00FF", icon="🎁", user=user)

    html = as_category_options([cat1, cat2], selected_id=cat2.id)

    assert f'value="{cat1.id}"' in html
    assert f'value="{cat2.id}"' in html
    assert 'selected' in html
    assert escape(cat1.name) in html
    assert escape(cat2.name) in html

# ---------- Ordering ----------
def test_categories_order_by_name(user):
    Category.objects.create(name="Zoo", type="EXPENSE", color="#333", icon="🦓", user=user)
    Category.objects.create(name="Apple", type="EXPENSE", color="#111", icon="🍎", user=user)
    Category.objects.create(name="Money", type="EXPENSE", color="#222", icon="💵", user=user)

    categories = Category.objects.filter(user=user).all()
    names = [cat.name for cat in categories]
    assert names == sorted(names)
