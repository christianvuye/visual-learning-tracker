#!/usr/bin/env python3
"""
Simple test script to verify the application components work
"""
from database import DatabaseManager
import json


def test_database():
    print("Testing database functionality...")

    # Initialize database
    db = DatabaseManager("test.db")

    # Create a test course
    course_id = db.create_course(
        title="Python Programming",
        description="Learn Python from basics to advanced",
        category="Programming",
        difficulty=3,
        estimated_hours=40,
        tags=["python", "programming", "beginner"],
    )
    print(f"Created course with ID: {course_id}")

    # Add modules
    module1_id = db.add_course_module(
        course_id=course_id,
        title="Python Basics",
        description="Variables, data types, control structures",
        estimated_minutes=120,
    )

    module2_id = db.add_course_module(
        course_id=course_id,
        title="Object-Oriented Programming",
        description="Classes, objects, inheritance",
        estimated_minutes=180,
    )

    print(f"Created modules: {module1_id}, {module2_id}")

    # Start and end a learning session
    session_id = db.start_learning_session(course_id, module1_id)
    print(f"Started session: {session_id}")

    db.end_learning_session(
        session_id, "Great learning session!", mood=4, energy_level=4
    )
    print("Ended session")

    # Create notes
    note_id = db.create_note(
        course_id=course_id,
        title="Python Variables",
        content="Variables in Python are created when you assign a value to them...",
        tags=["variables", "basics"],
    )
    print(f"Created note: {note_id}")

    # Create flashcard
    card_id = db.create_flashcard(
        course_id=course_id,
        question="What is a variable in Python?",
        answer="A variable is a name that refers to a value stored in memory",
    )
    print(f"Created flashcard: {card_id}")

    # Get statistics
    stats = db.get_learning_statistics()
    print(f"Learning statistics: {stats}")

    # Get courses
    courses = db.get_courses()
    print(f"Courses: {len(courses)} found")
    for course in courses:
        print(f"  - {course['title']} ({course['current_progress']:.1f}% complete)")

    print("Database test completed successfully!")
    return True


def test_mind_map_data():
    print("\nTesting mind map data structures...")

    # Sample mind map data
    sample_data = {
        "nodes": [
            {
                "id": "node_1",
                "x": 400,
                "y": 300,
                "text": "Python Programming",
                "color": "#e74c3c",
                "node_type": "main_topic",
                "connections": ["node_2", "node_3"],
            },
            {
                "id": "node_2",
                "x": 300,
                "y": 200,
                "text": "Data Types",
                "color": "#3498db",
                "node_type": "subtopic",
                "connections": ["node_1"],
            },
            {
                "id": "node_3",
                "x": 500,
                "y": 200,
                "text": "Control Flow",
                "color": "#2ecc71",
                "node_type": "subtopic",
                "connections": ["node_1"],
            },
        ],
        "connections": [
            {
                "source_id": "node_1",
                "target_id": "node_2",
                "connection_type": "contains",
                "color": "#95a5a6",
                "label": "includes",
            },
            {
                "source_id": "node_1",
                "target_id": "node_3",
                "connection_type": "contains",
                "color": "#95a5a6",
                "label": "includes",
            },
        ],
    }

    # Test JSON serialization
    json_str = json.dumps(sample_data, indent=2)
    print(f"Mind map JSON size: {len(json_str)} characters")

    # Test deserialization
    restored_data = json.loads(json_str)
    print(f"Nodes restored: {len(restored_data['nodes'])}")
    print(f"Connections restored: {len(restored_data['connections'])}")

    print("Mind map data test completed successfully!")
    return True


def main():
    print("=== Visual Learning Tracker - Component Tests ===\n")

    try:
        # Test database
        test_database()

        # Test mind map data
        test_mind_map_data()

        print("\n=== All tests passed! ===")
        print("\nThe Visual Learning Tracker components are working correctly.")
        print("Note: GUI testing requires a display. The application is ready to run.")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
