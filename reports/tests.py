import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from transactions.models import Transaction
from categories.models import Category
from datetime import date

@pytest.mark.django_db
def test_report_dashboard_authenticated(client):
    user = User.objects.create_user(username='testuser', password='12345')
    client.login(username='testuser', password='12345')
    response = client.get(reverse('report_dashboard'))

    assert response.status_code == 200
    assert 'Reports' in response.content.decode()

@pytest.mark.django_db
def test_report_dashboard_unauthenticated(client):
    response = client.get(reverse('report_dashboard'))
    assert response.status_code == 302

@pytest.mark.django_db
def test_monthly_report_view(client):
    user = User.objects.create_user(username='testuser', password='12345')
    category = Category.objects.create(user=user, name='Test Category', color='#FFFFFF')
    Transaction.objects.create(
        user=user, title='Test Income', type='INCOME', 
        category=category, amount=100, date=date.today()
    )

    client.login(username='testuser', password='12345')
    response = client.get(reverse('monthly_report'))

    assert response.status_code == 200
    assert 'Test Income' in response.content.decode()
    assert '100' in response.content.decode()


@pytest.mark.django_db
def test_export_data_csv(client):
    user = User.objects.create_user(username='testuser', password='12345')
    Transaction.objects.create(
        user=user, title='Salary', type='INCOME', 
        amount=1000, date=date.today()
    )

    client.login(username='testuser', password='12345')
    response = client.get(reverse('export_data'))

    assert response.status_code == 200
    assert 'text/csv' in response['Content-Type']
    assert 'Salary' in response.content.decode()
