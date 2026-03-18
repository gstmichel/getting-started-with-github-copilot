import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset activities data before each test."""
    # Store original activities
    original_activities = activities.copy()
    yield
    # Reset to original after test
    activities.clear()
    activities.update(original_activities)


def test_root_redirect(client):
    """Test that GET / redirects to /static/index.html."""
    # Arrange
    # (client fixture provides TestClient)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test that GET /activities returns the activities dictionary."""
    # Arrange
    # (activities are reset by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate(client):
    """Test that duplicate signup is prevented."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity(client):
    """Test signup for non-existent activity."""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_delete_participant_success(client):
    """Test successful deletion of a participant."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Exists in initial data

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert email not in activities[activity_name]["participants"]


def test_delete_participant_not_found(client):
    """Test deletion of non-existent participant."""
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_delete_participant_invalid_activity(client):
    """Test deletion from non-existent activity."""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]