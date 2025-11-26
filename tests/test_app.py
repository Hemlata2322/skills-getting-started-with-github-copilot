"""
Test suite for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "ava@mergington.edu"]
        },
        "Drama Club": {
            "description": "Learn acting and perform in theatrical productions",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, reset_activities):
        """Test that get activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that get activities returns all activities"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
    
    def test_activity_has_required_fields(self, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_activity_participants_is_list(self, reset_activities):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        assert isinstance(activities["Chess Club"]["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_returns_200(self, reset_activities):
        """Test signing up a new participant returns 200"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_adds_participant_to_activity(self, reset_activities):
        """Test that signup adds the participant to the activity"""
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant_returns_400(self, reset_activities):
        """Test that signing up an already registered participant returns 400"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, reset_activities):
        """Test signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_returns_success_message(self, reset_activities):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=student@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "student@mergington.edu" in data["message"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_returns_200(self, reset_activities):
        """Test unregistering an existing participant returns 200"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister removes the participant from the activity"""
        client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant_returns_400(self, reset_activities):
        """Test unregistering a non-existent participant returns 400"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_returns_404(self, reset_activities):
        """Test unregistering from a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_returns_success_message(self, reset_activities):
        """Test that unregister returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]


class TestIntegration:
    """Integration tests"""
    
    def test_signup_then_unregister_flow(self, reset_activities):
        """Test the complete signup and unregister flow"""
        # Sign up
        response = client.post(
            "/activities/Programming%20Class/signup?email=integration@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant added
        response = client.get("/activities")
        assert "integration@mergington.edu" in response.json()["Programming Class"]["participants"]
        
        # Unregister
        response = client.post(
            "/activities/Programming%20Class/unregister?email=integration@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant removed
        response = client.get("/activities")
        assert "integration@mergington.edu" not in response.json()["Programming Class"]["participants"]
    
    def test_multiple_signups(self, reset_activities):
        """Test multiple participants signing up for the same activity"""
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Art%20Studio/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all participants added
        response = client.get("/activities")
        participants = response.json()["Art Studio"]["participants"]
        for email in emails:
            assert email in participants
