from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_store

INITIAL_ACTIVITIES = deepcopy(activities_store)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities_store.clear()
    activities_store.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    activities_store.clear()
    activities_store.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity in data
    assert "participants" in data[expected_activity]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    before_count = len(activities_store[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Signed up {email} for {activity_name}"
    assert len(activities_store[activity_name]["participants"]) == before_count + 1
    assert email in activities_store[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    before_count = len(activities_store[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Removed {email} from {activity_name}"
    assert len(activities_store[activity_name]["participants"]) == before_count - 1
    assert email not in activities_store[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "notfound@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={missing_email}")
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Participant not found"


def test_root_redirects_to_static_index():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (301, 302, 303, 307, 308)
    assert response.headers["location"] == "/static/index.html"
