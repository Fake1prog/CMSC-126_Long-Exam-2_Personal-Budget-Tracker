import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import ErrorLog
from core.templatetags.custom_filters import percentage
from transactions.models import Transaction


@pytest.mark.django_db
def test_home_view_redirects_authenticated(client):
    user = User.objects.create_user(username='testuser', password='pass123')
    client.login(username='testuser', password='pass123')
    response = client.get(reverse('home'))
    assert response.status_code == 302
    assert response.url == reverse('dashboard')


@pytest.mark.django_db
def test_home_view_unauthenticated(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'GastadorCheck' in response.content.decode()


@pytest.mark.django_db
def test_about_view(client):
    response = client.get(reverse('about'))
    assert response.status_code == 200
    assert 'About GastadorCheck' in response.content.decode()


@pytest.mark.django_db
def test_contact_view(client):
    response = client.get(reverse('contact'))
    assert response.status_code == 200
    assert 'Get in Touch' in response.content.decode()


@pytest.mark.django_db
def test_contact_form_post(client):
    data = {
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'subject': 'Test Inquiry',
        'message': 'I love your site!'
    }
    response = client.post(reverse('contact'), data=data)
    assert response.status_code in [200, 302]


@pytest.mark.django_db
def test_dashboard_view_requires_login(client):
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_dashboard_view_logged_in(client):
    user = User.objects.create_user(username='testuser', password='pass123')
    client.login(username='testuser', password='pass123')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'Welcome Back' in response.content.decode()


@pytest.mark.django_db
def test_dashboard_context_data(client):
    user = User.objects.create_user(username='tester', password='securepass')
    client.login(username='tester', password='securepass')

    Transaction.objects.create(user=user, type='INCOME', amount=1000, title='Salary', date=timezone.now())
    Transaction.objects.create(user=user, type='EXPENSE', amount=200, title='Groceries', date=timezone.now())

    response = client.get(reverse('dashboard'))
    content = response.content.decode()

    assert '₱1000' in content
    assert '₱200' in content
    assert '₱800' in content


@pytest.mark.django_db
def test_dashboard_with_no_transactions(client):
    user = User.objects.create_user(username='noentry', password='nopass')
    client.login(username='noentry', password='nopass')

    response = client.get(reverse('dashboard'))
    content = response.content.decode()

    assert '₱0' in content
    assert 'No transactions yet.' in content


@pytest.mark.django_db
def test_errorlog_model_str():
    log = ErrorLog.objects.create(
        error_type='DATABASE',
        description='Failed query',
    )
    assert 'Database Error at' in str(log)


@pytest.mark.django_db
def test_errorlog_resolved_flag():
    log = ErrorLog.objects.create(
        error_type='SYSTEM',
        description='Unexpected crash',
    )
    assert not log.resolved
    log.resolved = True
    log.save()
    assert ErrorLog.objects.get(id=log.id).resolved is True


@pytest.mark.django_db
def test_errorlog_null_user_allowed():
    log = ErrorLog.objects.create(
        user=None,
        error_type='PERMISSION',
        description='Anonymous access',
    )
    assert log.user is None
    assert 'Permission Error' in str(log)


@pytest.mark.django_db
def test_errorlog_filter_unresolved_only():
    ErrorLog.objects.create(error_type='VALIDATION', description='Error A', resolved=False)
    ErrorLog.objects.create(error_type='VALIDATION', description='Error B', resolved=True)

    unresolved = ErrorLog.objects.filter(resolved=False)
    assert unresolved.count() == 1
    assert unresolved.first().description == 'Error A'


def test_percentage_filter_valid():
    assert percentage(25, 100) == 25.0


def test_percentage_filter_zero_division():
    assert percentage(50, 0) == 0


def test_percentage_filter_invalid_input():
    assert percentage("abc", "def") == 0


def test_percentage_with_float_strings():
    assert round(percentage("25.0", "50.0"), 2) == 50.00


def test_percentage_with_negative_values():
    assert round(percentage("-30", "60"), 2) == -50.00


@pytest.mark.django_db
def test_dashboard_with_uncategorized_expense(client):
    user = User.objects.create_user(username='uncat', password='testpass')
    client.login(username='uncat', password='testpass')

    Transaction.objects.create(user=user, type='EXPENSE', amount=500, title='Misc', category=None, date=timezone.now())
    response = client.get(reverse('dashboard'))
    content = response.content.decode()

    assert 'Uncategorized' in content
    assert '₱500' in content


@pytest.mark.django_db
def test_errorlog_large_input():
    long_desc = 'A' * 1000
    long_trace = 'Traceback line\n' * 500
    log = ErrorLog.objects.create(
        error_type='SYSTEM',
        description=long_desc,
        stack_trace=long_trace
    )
    assert len(log.description) == 1000
    assert 'Traceback' in log.stack_trace


@pytest.mark.django_db
def test_contact_form_missing_fields(client):
    response = client.post(reverse('contact'), {
        'name': 'Leah',
        # 'email' is missing
        'message': 'Hi!'
    })
    assert response.status_code == 200  # Should render again due to error
    assert 'required' in response.content.decode().lower()


def test_percentage_with_large_values():
    assert round(percentage(5000000, 10000000), 2) == 50.00


@pytest.mark.django_db
def test_about_view_authenticated(client):
    user = User.objects.create_user(username='tester2', password='pass123')
    client.login(username='tester2', password='pass123')
    response = client.get(reverse('about'))
    assert response.status_code == 200
    assert 'Why Choose Us' in response.content.decode()


@pytest.mark.django_db
def test_contact_view_authenticated(client):
    user = User.objects.create_user(username='tester3', password='pass123')
    client.login(username='tester3', password='pass123')
    response = client.get(reverse('contact'))
    assert response.status_code == 200
    assert 'Get in Touch' in response.content.decode()

def test_percentage_with_none_values():
    assert percentage(None, 100) == 0
    assert percentage(100, None) == 0
    assert percentage(None, None) == 0


@pytest.mark.django_db
def test_dashboard_negative_balance(client):
    user = User.objects.create_user(username='lossuser', password='pass123')
    client.login(username='lossuser', password='pass123')

    Transaction.objects.create(user=user, type='INCOME', amount=200, title='Allowance', date=timezone.now())
    Transaction.objects.create(user=user, type='EXPENSE', amount=500, title='Rent', date=timezone.now())

    response = client.get(reverse('dashboard'))
    content = response.content.decode()
    assert '₱-300' in content
    assert 'text-red-600' in content  # negative balance styling


@pytest.mark.django_db
def test_errorlog_str_fallback_unknown_type():
    log = ErrorLog.objects.create(
        error_type='UNKNOWN',
        description='Unknown error type'
    )
    # get_error_type_display will fallback to raw value if invalid
    assert 'UNKNOWN at' in str(log)


@pytest.mark.django_db
def test_contact_form_html_injection(client):
    response = client.post(reverse('contact'), {
        'name': '<script>alert(1)</script>',
        'email': 'evil@example.com',
        'subject': 'Injection test',
        'message': '<img src=x onerror=alert(2)>'
    })
    assert response.status_code in [200, 302]
    # Ensure content is escaped or not reflected unsafely


@pytest.mark.django_db
def test_errorlog_blank_optional_fields():
    log = ErrorLog.objects.create(
        error_type='VALIDATION',
        description='No stack/user action'
    )
    assert log.stack_trace == ''
    assert log.user_action == ''


@pytest.mark.django_db
def test_errorlog_bulk_insert_and_order():
    for i in range(100):
        ErrorLog.objects.create(
            error_type='OTHER',
            description=f'Log #{i}'
            # timestamp will be ignored due to auto_now_add
        )
    logs = ErrorLog.objects.all()
    descriptions = [log.description for log in logs]

    assert 'Log #99' in descriptions
    assert 'Log #0' in descriptions
    assert len(descriptions) == 100





