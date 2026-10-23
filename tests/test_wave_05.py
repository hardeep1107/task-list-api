from app.models.goal import Goal
import pytest

def test_goal_to_dict():
    #Arrange
    new_goal = Goal(id=1, title="Seize the Day!")
    
    #Act
    goal_dict = new_goal.to_dict()

    #Assert
    assert goal_dict["id"] == 1
    assert goal_dict["title"] == "Seize the Day!"

def test_goal_to_dict_no_id():
    #Arrange
    new_goal = Goal(title="Seize the Day!")
    
    #Act
    goal_dict = new_goal.to_dict()

    #Assert
    assert goal_dict["id"] is None
    assert goal_dict["title"] == "Seize the Day!"

def test_goal_to_dict_no_title():
    #Arrange
    new_goal = Goal(id=1)
    
    #Act
    goal_dict = new_goal.to_dict()

    #Assert
    assert goal_dict["id"] == 1
    assert goal_dict["title"] is None

def test_goal_from_dict():
    #Arrange
    goal_dict =  {
        "title": "Seize the Day!",
    }

    #Act
    goal_obj =  Goal.from_dict(goal_dict)

    #Assert
    assert goal_obj.title == "Seize the Day!"

def test_goal_from_dict_no_title():
    #Arrange
    goal_dict =  {
    }

    #Act & Assert
    with pytest.raises(KeyError, match = 'title'):
        Goal.from_dict(goal_dict)

def test_get_goals_no_saved_goals(client):
    # Act
    response = client.get("/goals")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == []

def test_get_goals_one_saved_goal(client, one_goal):
    # Act
    response = client.get("/goals")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [
        {
            "id": 1,
            "title": "Build a habit of going outside daily"
        }
    ]

def test_get_goal(client, one_goal):
    # Act
    response = client.get("/goals/1")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == {
        "id": 1,
        "title": "Build a habit of going outside daily"
    }

def test_get_goal_not_found(client):
    # Act
    response = client.get("/goals/99999")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert response_body == {"message": "goal 99999 not found"}

def test_create_goal(client):
    # Act
    response = client.post("/goals", json={
        "title": "My New Goal"
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 201
    assert response_body == {
        "id": 1,
        "title": "My New Goal"
    }

def test_update_goal(client, one_goal):
    # Arrange
    goal_id = one_goal.id
    request_body = {"title": "Learn Flask APIs"}

    # Act
    response = client.put(
        f"/goals/{goal_id}",
        json=request_body
    )

    # Assert
    assert response.status_code == 204
    assert response.mimetype == "application/json"

    updated_goal = client.get(f"/goals/{goal_id}")
    assert updated_goal.get_json()["title"] == "Learn Flask APIs"

def test_update_goal_not_found(client):
    # Arrange
    request_body = {"title": "Learn Flask APIs"}

    # Act
    response = client.put("/goals/99999", json=request_body)
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert response_body == {"message": "goal 99999 not found"}

def test_delete_goal(client, one_goal):
    # Act
    response = client.delete(f"/goals/{one_goal.id}")

    # Assert
    assert response.status_code == 204
    assert response.mimetype == "application/json"

    # Check that the goal was deleted
    response = client.get(f"/goals/{one_goal.id}")
    assert response.status_code == 404

    response_body = response.get_json()
    assert "message" in response_body
    assert response_body["message"] == f"goal {one_goal.id} not found"

def test_delete_goal_not_found(client):
    # Act
    response = client.delete("/goals/99999")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert response_body["message"] == "goal 99999 not found"

def test_create_goal_missing_title(client):
    # Act
    response = client.post("/goals", json={})
    response_body = response.get_json()

    # Assert
    assert response.status_code == 400
    assert response_body == {
        "details": "Invalid data"
    }
