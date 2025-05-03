import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile



@pytest.mark.django_db
def test_user_registration(client):
    registration_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password1': 'strongpassword123',
        'password2': 'strongpassword123',
    }
    response = client.post(reverse('register'), data=registration_data)
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert User.objects.filter(username='testuser').exists()


@pytest.mark.django_db
def test_user_login(client, django_user_model):
    django_user_model.objects.create_user(username='tester', password='pass1234')
    response = client.post(reverse('login'), {'username': 'tester', 'password': 'pass1234'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_user_logout(client, django_user_model):
    django_user_model.objects.create_user(username='tester', password='pass1234')
    client.login(username='tester', password='pass1234')
    response = client.post(reverse('logout'))  # <-- FIXED
    assert response.status_code == 302
    assert response.url == reverse('home')



@pytest.mark.django_db
def test_profile_requires_login(client):
    response = client.get(reverse('profile'))
    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))


@pytest.mark.django_db
def test_profile_access_and_update(client, django_user_model):
    user = django_user_model.objects.create_user(username='tester', password='pass1234', email='old@email.com')
    client.login(username='tester', password='pass1234')

    response = client.get(reverse('profile'))
    assert response.status_code == 200
    assert "Profile" in response.content.decode()


    update_data = {
        'username': 'tester',
        'email': 'new@email.com',
        'default_currency': 'PHP',
        'date_format_preference': 'MM/DD/YYYY'
    }
    response = client.post(reverse('profile'), data=update_data)
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.email == 'new@email.com'


@pytest.mark.django_db
def test_duplicate_username_registration(client):
    User.objects.create_user(username='existinguser', email='old@mail.com', password='pass1234')
    data = {
        'username': 'existinguser',
        'email': 'new@mail.com',
        'password1': 'strongpass123',
        'password2': 'strongpass123',
    }
    response = client.post(reverse('register'), data=data)
    assert response.status_code == 200
    assert "A user with that username already exists." in response.content.decode()


@pytest.mark.django_db
def test_invalid_login_attempt(client):
    response = client.post(reverse('login'), {'username': 'ghost', 'password': 'wrongpass'})
    assert response.status_code == 200
    assert "Please enter a correct username and password" in response.content.decode()


@pytest.mark.django_db
def test_profile_page_displays_user_data(client, django_user_model):
    user = django_user_model.objects.create_user(username='leah', password='testpass', email='leah@mail.com')
    client.login(username='leah', password='testpass')
    response = client.get(reverse('profile'))

    content = response.content.decode()
    assert 'leah@mail.com' in content
    assert 'Philippine Peso (PHP)' in content


@pytest.mark.django_db
def test_profile_update_invalid_email(client, django_user_model):
    django_user_model.objects.create_user(username='tester', password='pass1234', email='valid@mail.com')
    client.login(username='tester', password='pass1234')
    invalid_data = {
        'username': 'tester',
        'email': 'not-an-email',
        'default_currency': 'PHP',
        'date_format_preference': 'MM/DD/YYYY'
    }
    response = client.post(reverse('profile'), data=invalid_data)

    assert response.status_code == 200
    assert "Enter a valid email address." in response.content.decode()


@pytest.mark.django_db
def test_profile_signal_creates_profile():
    user = User.objects.create_user(username='newbie', email='x@mail.com', password='pass123')
    assert hasattr(user, 'profile')
    assert isinstance(user.profile, Profile)
    assert user.profile.default_currency == 'USD'


@pytest.mark.django_db
def test_registration_password_mismatch(client):
    data = {
        'username': 'testmismatch',
        'email': 'test@example.com',
        'password1': 'password123',
        'password2': 'wrongpass123',
    }
    response = client.post(reverse('register'), data=data)
    assert response.status_code == 200
    assert "The two password fields didn’t match." in response.content.decode()


@pytest.mark.django_db
def test_registration_missing_fields(client):
    response = client.post(reverse('register'), data={})
    assert response.status_code == 200
    assert "This field is required." in response.content.decode()


@pytest.mark.django_db
def test_username_case_sensitivity(client, django_user_model):
    django_user_model.objects.create_user(username='LeahTenebroso', password='secret123')
    response = client.post(reverse('login'), {'username': 'leahtenebroso', 'password': 'secret123'})
    assert response.status_code == 200
    assert "Please enter a correct username and password" in response.content.decode()


@pytest.mark.django_db
def test_profile_signal_on_user_update(django_user_model):
    user = django_user_model.objects.create_user(username='signaluser', password='test1234')
    user.email = 'updated@mail.com'
    user.save()
    assert hasattr(user, 'profile')
    assert user.profile.default_currency == 'USD'

@pytest.mark.django_db
def test_registration_with_common_password(client):
    data = {
        'username': 'commonpassuser',
        'email': 'common@example.com',
        'password1': 'password123',  # Common password
        'password2': 'password123',
    }
    response = client.post(reverse('register'), data=data)
    assert response.status_code == 200
    assert "This password is too common." in response.content.decode()


@pytest.mark.django_db
def test_registration_with_numeric_password(client):
    data = {
        'username': 'numericuser',
        'email': 'numeric@example.com',
        'password1': '12345678',  # Numeric only
        'password2': '12345678',
    }
    response = client.post(reverse('register'), data=data)
    assert response.status_code == 200
    assert "This password" in response.content.decode() or "Password" in response.content.decode()



@pytest.mark.django_db
def test_registration_with_short_password(client):
    data = {
        'username': 'shortpass',
        'email': 'short@example.com',
        'password1': 'a1b2c3',
        'password2': 'a1b2c3',
    }
    response = client.post(reverse('register'), data=data)
    assert response.status_code == 200
    assert "This password is too short." in response.content.decode()


@pytest.mark.django_db
def test_registration_with_similar_password(client):
    data = {
        'username': 'similaruser',
        'email': 'similar@example.com',
        'password1': 'similaruser123',
        'password2': 'similaruser123',
    }
    response = client.post(reverse('register'), data=data)
    assert response.status_code == 200
    assert "The password is too similar to the username." in response.content.decode()


