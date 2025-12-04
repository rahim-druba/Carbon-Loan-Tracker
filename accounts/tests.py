import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_user_roles():
    citizen = User.objects.create_user('c', 'c@e.com', 'pass', role=User.Role.CITIZEN)
    agent = User.objects.create_user('a', 'a@e.com', 'pass', role=User.Role.AGENT)
    
    assert citizen.is_citizen()
    assert not citizen.is_agent()
    assert agent.is_agent()
    assert not agent.is_citizen()
