"""Initial database schema."""

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True, default='check-circle'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )

    # Create topics table
    op.create_table(
        'topics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('order_num', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create quizzes table
    op.create_table(
        'quizzes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True, default=''),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quiz_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('option_a', sa.String(), nullable=False),
        sa.Column('option_b', sa.String(), nullable=False),
        sa.Column('option_c', sa.String(), nullable=False),
        sa.Column('option_d', sa.String(), nullable=False),
        sa.Column('correct_option', sa.String(), nullable=False),
        sa.Column('explanation', sa.String(), nullable=True, default=''),
        sa.Column('order_num', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create quiz_results table
    op.create_table(
        'quiz_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('quiz_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create glossary table
    op.create_table(
        'glossary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('term', sa.String(), nullable=False),
        sa.Column('definition', sa.Text(), nullable=False),
        sa.Column('letter', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('term')
    )

    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True, default=''),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_progress table
    op.create_table(
        'user_progress',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('topics_read', sa.Integer(), nullable=True, default=0),
        sa.Column('quizzes_passed', sa.Integer(), nullable=True, default=0),
        sa.Column('total_score', sa.Integer(), nullable=True, default=0),
        sa.Column('last_visit', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )

    # Create read_topics table
    op.create_table(
        'read_topics',
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('session_id', 'topic_id')
    )

    # Create bookmarks table
    op.create_table(
        'bookmarks',
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('bookmarked_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('session_id', 'topic_id'),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE')
    )

    # Create admin_sessions table
    op.create_table(
        'admin_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('expires', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create admin_users table
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

    # Create indexes
    op.create_index('ix_categories_id', 'categories', ['id'])
    op.create_index('ix_categories_slug', 'categories', ['slug'])
    op.create_index('ix_topics_id', 'topics', ['id'])
    op.create_index('ix_quizzes_id', 'quizzes', ['id'])
    op.create_index('ix_questions_id', 'questions', ['id'])
    op.create_index('ix_glossary_id', 'glossary', ['id'])
    op.create_index('ix_admin_users_username', 'admin_users', ['username'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_admin_users_username', table_name='admin_users')
    op.drop_index('ix_glossary_id', table_name='glossary')
    op.drop_index('ix_questions_id', table_name='questions')
    op.drop_index('ix_quizzes_id', table_name='quizzes')
    op.drop_index('ix_topics_id', table_name='topics')
    op.drop_index('ix_categories_slug', table_name='categories')
    op.drop_index('ix_categories_id', table_name='categories')

    op.drop_table('admin_users')
    op.drop_table('notifications')
    op.drop_table('comments')
    op.drop_table('admin_sessions')
    op.drop_table('bookmarks')
    op.drop_table('read_topics')
    op.drop_table('user_progress')
    op.drop_table('feedback')
    op.drop_table('glossary')
    op.drop_table('quiz_results')
    op.drop_table('questions')
    op.drop_table('quizzes')
    op.drop_table('topics')
    op.drop_table('categories')
