"""
Tests for the High School Management System API

These tests verify the functionality of the FastAPI application endpoints
for managing extracurricular activities.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client to make requests to the application
client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self):
        """Test that the root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns the activities dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_contains_expected_fields(self):
        """Test that each activity contains the expected fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_are_list(self):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data["Chess Club"]["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self):
        """Test successful signup of a new student"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_student_to_participants(self):
        """Test that signup actually adds the student to the participants list"""
        email = "teststudent@mergington.edu"
        client.post(
            "/activities/Soccer Club/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        data = response.json()
        assert email in data["Soccer Club"]["participants"]

    def test_signup_duplicate_student_fails(self):
        """Test that signing up an already registered student fails"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signup to a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_existing_student_success(self):
        """Test successful unregistration of a student"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_student_from_participants(self):
        """Test that unregister actually removes the student"""
        email = "daniel@mergington.edu"  # Already in Chess Club
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_nonregistered_student_fails(self):
        """Test that unregistering a non-registered student fails"""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregistering from a non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
