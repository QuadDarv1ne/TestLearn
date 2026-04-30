#!/usr/bin/env python3
"""
Database initialization and seeding script.
Run this to set up the database with initial data.
"""

from app.db.database import SessionLocal, Base
from app.db.models import (
    Category, Topic, Quiz, Question, GlossaryTerm, 
    AchievementDefinition
)


def init_database():
    """Initialize database tables and seed with sample data."""
    
    # Create all tables
    Base.metadata.create_all(bind=SessionLocal().bind)
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Category).count() > 0:
            print("Database already initialized. Skipping seed.")
            return
        
        # Seed Categories
        categories = [
            Category(
                name='Python Basics',
                slug='python-basics',
                description='Fundamental Python programming concepts',
                icon='🐍'
            ),
            Category(
                name='Web Development',
                slug='web-dev',
                description='FastAPI and modern web frameworks',
                icon='🌐'
            ),
            Category(
                name='Data Science',
                slug='data-science',
                description='Data analysis and machine learning',
                icon='📊'
            ),
            Category(
                name='DevOps',
                slug='devops',
                description='CI/CD, containers, and deployment',
                icon='🚀'
            )
        ]
        db.add_all(categories)
        db.commit()
        
        # Seed Topics
        python_cat = db.query(Category).filter_by(slug='python-basics').first()
        web_cat = db.query(Category).filter_by(slug='web-dev').first()
        
        topics = [
            Topic(category_id=python_cat.id, title='Variables and Data Types', content='Learn about strings, integers, lists, and dictionaries in Python.', order_num=1),
            Topic(category_id=python_cat.id, title='Control Flow', content='Master if statements, loops, and conditional logic.', order_num=2),
            Topic(category_id=python_cat.id, title='Functions', content='Create reusable code with functions and lambda expressions.', order_num=3),
            Topic(category_id=web_cat.id, title='REST API Basics', content='Understanding HTTP methods, endpoints, and status codes.', order_num=1),
            Topic(category_id=web_cat.id, title='FastAPI Introduction', content='Build fast APIs with Python type hints.', order_num=2),
        ]
        db.add_all(topics)
        db.commit()
        
        # Seed Quizzes
        quiz = Quiz(
            category_id=python_cat.id,
            title='Python Basics Quiz',
            description='Test your knowledge of Python fundamentals'
        )
        db.add(quiz)
        db.commit()
        
        questions = [
            Question(quiz_id=quiz.id, question_text='What is the output of print(2 + 2)?', correct_option='B', option_a='2', option_b='4', option_c='22', option_d='Error'),
            Question(quiz_id=quiz.id, question_text='Which type is mutable?', correct_option='B', option_a='Tuple', option_b='List', option_c='String', option_d='Integer'),
            Question(quiz_id=quiz.id, question_text='How do you create a function?', correct_option='B', option_a='function myFunc()', option_b='def myFunc():', option_c='func myFunc()', option_d='create myFunc()'),
        ]
        db.add_all(questions)
        db.commit()
        
        # Seed Glossary Terms
        glossary_terms = [
            GlossaryTerm(term='API', definition='Application Programming Interface - allows different software applications to communicate', letter='A'),
            GlossaryTerm(term='Async', definition='Asynchronous programming - executing tasks without blocking the main thread', letter='A'),
            GlossaryTerm(term='Backend', definition='Server-side application logic and database operations', letter='B'),
            GlossaryTerm(term='Database', definition='Organized collection of structured information stored electronically', letter='D'),
            GlossaryTerm(term='Endpoint', definition='A specific path in an API that accepts requests', letter='E'),
            GlossaryTerm(term='FastAPI', definition='Modern Python web framework for building APIs quickly', letter='F'),
            GlossaryTerm(term='HTTP', definition='Hypertext Transfer Protocol - foundation of data communication on the web', letter='H'),
            GlossaryTerm(term='JSON', definition='JavaScript Object Notation - lightweight data interchange format', letter='J'),
        ]
        db.add_all(glossary_terms)
        db.commit()
        
        # Seed Achievements
        achievements = [
            AchievementDefinition(name='First Steps', description='Complete your first quiz', icon='🎯', category='quiz', requirement_type='count', requirement_value=1, xp_reward=10),
            AchievementDefinition(name='Quick Learner', description='Score 100% on any quiz', icon='⚡', category='quiz', requirement_type='percentage', requirement_value=100, xp_reward=25),
            AchievementDefinition(name='Knowledge Seeker', description='Read 10 theory topics', icon='📚', category='topic', requirement_type='count', requirement_value=10, xp_reward=50),
            AchievementDefinition(name='Streak Master', description='Maintain a 7-day learning streak', icon='🔥', category='streak', requirement_type='count', requirement_value=7, xp_reward=100),
            AchievementDefinition(name='Expert', description='Complete all quizzes in a category', icon='🏆', category='quiz', requirement_type='special', requirement_value=0, xp_reward=200),
        ]
        db.add_all(achievements)
        db.commit()
        
        print(f"✅ Database initialized successfully!")
        print(f"   - {len(categories)} categories")
        print(f"   - {len(topics)} topics")
        print(f"   - {len(questions)} quiz questions")
        print(f"   - {len(glossary_terms)} glossary terms")
        print(f"   - {len(achievements)} achievements")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    init_database()
