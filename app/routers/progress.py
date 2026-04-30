"""
User Progress API router
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, UTC
import uuid
import io
from typing import List

from app.db.database import get_db
from app.db.models import UserProgress, ReadTopic, Bookmark, QuizResult
from app.schemas import UserProgressResponse

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

router = APIRouter()


@router.post("/xp")
def add_experience(amount: int = 10, session_id: str = None, request: Request = None, db: Session = Depends(get_db)):
    """Add experience points to user progress."""
    # Get session_id from parameter or request cookie
    if not session_id and request:
        session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())

    # Get or create user progress
    progress = db.query(UserProgress).filter(UserProgress.session_id == session_id).first()

    if not progress:
        progress = UserProgress(
            id=str(uuid.uuid4()),
            session_id=session_id,
            topics_read=0,
            quizzes_passed=0,
            total_score=amount,
            last_visit=datetime.now(UTC)
        )
        db.add(progress)
    else:
        progress.total_score += amount
        progress.last_visit = datetime.now(UTC)

    db.commit()
    db.refresh(progress)

    # Calculate level
    experience = progress.total_score
    level = 1
    xp_required = 100
    total_xp = experience
    while total_xp >= xp_required:
        total_xp -= xp_required
        level += 1
        xp_required = int(xp_required * 1.5)

    return {
        "status": "success",
        "session_id": session_id,
        "total_score": progress.total_score,
        "level": level,
        "experience": total_xp,
        "xp_required_for_next_level": xp_required
    }


@router.get("", response_model=UserProgressResponse)
def get_user_progress(request: Request, db: Session = Depends(get_db)):
    """Get current user's progress."""
    session_id = request.cookies.get("session_id")

    if not session_id:
        # Create a new session if none exists
        import uuid
        from datetime import datetime, UTC

        session_id = str(uuid.uuid4())
        progress = UserProgress(
            id=str(uuid.uuid4()),
            session_id=session_id,
            topics_read=0,
            quizzes_passed=0,
            total_score=0,
            last_visit=datetime.now(UTC)
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    progress = db.query(UserProgress).filter(UserProgress.session_id == session_id).first()

    if not progress:
        # Create new progress record
        import uuid
        from datetime import datetime, UTC

        progress = UserProgress(
            id=str(uuid.uuid4()),
            session_id=session_id,
            topics_read=0,
            quizzes_passed=0,
            total_score=0,
            last_visit=datetime.now(UTC)
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    # Calculate level and experience
    experience = progress.total_score
    level = 1
    xp_required = 100
    total_xp = experience

    while total_xp >= xp_required:
        total_xp -= xp_required
        level += 1
        xp_required = int(xp_required * 1.5)

    return {
        "id": progress.id,
        "session_id": progress.session_id,
        "topics_read": progress.topics_read,
        "quizzes_passed": progress.quizzes_passed,
        "total_score": progress.total_score,
        "last_visit": progress.last_visit.isoformat() if progress.last_visit else None,
        "level": level,
        "experience": experience
    }


@router.post("/mark-topic-read")
def mark_topic_read(topic_id: int, request: Request, db: Session = Depends(get_db)):
    """Mark a topic as read for the current user."""
    session_id = request.cookies.get("session_id")

    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())

    from datetime import datetime, UTC

    # Check if already marked
    existing = db.query(ReadTopic).filter(
        ReadTopic.session_id == session_id,
        ReadTopic.topic_id == topic_id
    ).first()

    if not existing:
        read_topic = ReadTopic(
            session_id=session_id,
            topic_id=topic_id,
            read_at=datetime.now(UTC)
        )
        db.add(read_topic)

        # Update progress
        progress = db.query(UserProgress).filter(UserProgress.session_id == session_id).first()
        if progress:
            progress.topics_read += 1
            progress.last_visit = datetime.now(UTC)
        else:
            import uuid
            progress = UserProgress(
                id=str(uuid.uuid4()),
                session_id=session_id,
                topics_read=1,
                quizzes_passed=0,
                total_score=0,
                last_visit=datetime.now(UTC)
            )
            db.add(progress)

        db.commit()

    return {"status": "success", "session_id": session_id}


@router.get("/bookmarks", response_model=List[dict])
def get_bookmarks(request: Request, db: Session = Depends(get_db)):
    """Get user's bookmarks."""
    session_id = request.cookies.get("session_id")

    if not session_id:
        return []

    bookmarks = db.query(Bookmark).filter(Bookmark.session_id == session_id).all()

    result = []
    for bm in bookmarks:
        result.append({
            "topic_id": bm.topic_id,
            "bookmarked_at": bm.bookmarked_at.isoformat() if bm.bookmarked_at else None
        })

    return result


@router.post("/bookmarks/{topic_id}")
def add_bookmark(topic_id: int, request: Request, db: Session = Depends(get_db)):
    """Add a bookmark for a topic."""
    session_id = request.cookies.get("session_id")

    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())

    from datetime import datetime, UTC

    # Check if already bookmarked
    existing = db.query(Bookmark).filter(
        Bookmark.session_id == session_id,
        Bookmark.topic_id == topic_id
    ).first()

    if not existing:
        bookmark = Bookmark(
            session_id=session_id,
            topic_id=topic_id,
            bookmarked_at=datetime.now(UTC)
        )
        db.add(bookmark)
        db.commit()

    return {"status": "success", "session_id": session_id}


@router.delete("/bookmarks/{topic_id}")
def remove_bookmark(topic_id: int, request: Request, db: Session = Depends(get_db)):
    """Remove a bookmark for a topic."""
    session_id = request.cookies.get("session_id")

    if session_id:
        bookmark = db.query(Bookmark).filter(
            Bookmark.session_id == session_id,
            Bookmark.topic_id == topic_id
        ).first()

        if bookmark:
            db.delete(bookmark)
            db.commit()

    return {"status": "success"}


@router.get("/stats")
def get_progress_stats(request: Request, db: Session = Depends(get_db)):
    """Get user progress statistics including unlocked achievements and daily challenge."""
    session_id = request.cookies.get("session_id", "anonymous")

    # Get user progress
    progress = db.query(UserProgress).filter(
        UserProgress.session_id == session_id
    ).first()

    if not progress:
        # Return default stats for new user
        return {
            "user_progress": {
                "topics_read": 0,
                "quizzes_passed": 0,
                "total_score": 0,
                "level": 1,
                "experience": 0
            },
            "unlocked_achievements": [],
            "daily_challenge": None
        }

    # Calculate level and experience
    experience = progress.total_score
    level = 1
    xp_required = 100
    total_xp = experience

    while total_xp >= xp_required:
        total_xp -= xp_required
        level += 1
        xp_required = int(xp_required * 1.5)

    # Get unlocked achievements
    achievements = [
        {
            "id": 1,
            "name": "Первые шаги",
            "description": "Прочитать первую тему",
            "icon": "📚",
            "unlocked": progress.topics_read >= 1
        },
        {
            "id": 2,
            "name": "Любопытный",
            "description": "Прочитать 5 тем",
            "icon": "🔍",
            "unlocked": progress.topics_read >= 5
        },
        {
            "id": 3,
            "name": "Эрудит",
            "description": "Прочитать 10 тем",
            "icon": "🎓",
            "unlocked": progress.topics_read >= 10
        },
        {
            "id": 4,
            "name": "Новичок в тестировании",
            "description": "Пройти первый тест",
            "icon": "✅",
            "unlocked": progress.quizzes_passed >= 1
        },
        {
            "id": 5,
            "name": "Опытный тестировщик",
            "description": "Пройти 5 тестов",
            "icon": "🏆",
            "unlocked": progress.quizzes_passed >= 5
        },
        {
            "id": 6,
            "name": "Мастер тестирования",
            "description": "Набрать 100+ баллов",
            "icon": "👑",
            "unlocked": progress.total_score >= 100
        }
    ]

    unlocked_achievements = [a for a in achievements if a["unlocked"]]

    # Get daily challenge
    from sqlalchemy import func
    quiz = db.query(QuizResult).order_by(func.random()).first()

    daily_challenge = None
    if quiz:
        expires = datetime.now(UTC).replace(hour=23, minute=59, second=59)
        daily_challenge = {
            "id": 1,
            "quiz_id": quiz.quiz_id,
            "title": "Ежедневный вызов",
            "description": "Пройдите тест и получите 50 XP!",
            "bonus_xp": 50,
            "completed": False,
            "expires_at": expires.isoformat()
        }

    return {
        "user_progress": {
            "topics_read": progress.topics_read,
            "quizzes_passed": progress.quizzes_passed,
            "total_score": progress.total_score,
            "level": level,
            "experience": experience
        },
        "unlocked_achievements": unlocked_achievements,
        "daily_challenge": daily_challenge
    }


@router.get("/stats/export/pdf")
def export_progress_pdf(request: Request, db: Session = Depends(get_db)):
    """Export user progress as PDF report."""
    session_id = request.cookies.get("session_id", "anonymous")

    # Get user progress
    progress = db.query(UserProgress).filter(
        UserProgress.session_id == session_id
    ).first()

    if not progress:
        # For anonymous users or users without progress, create minimal report
        progress_data = {
            "topics_read": 0,
            "quizzes_passed": 0,
            "total_score": 0,
            "level": 1,
            "experience": 0,
            "last_visit": None
        }
        username = "Анонимный пользователь"
    else:
        # Calculate level and experience
        experience = progress.total_score
        level = 1
        xp_required = 100
        total_xp = experience

        while total_xp >= xp_required:
            total_xp -= xp_required
            level += 1
            xp_required = int(xp_required * 1.5)

        progress_data = {
            "topics_read": progress.topics_read,
            "quizzes_passed": progress.quizzes_passed,
            "total_score": progress.total_score,
            "level": level,
            "experience": experience,
            "last_visit": progress.last_visit
        }
        username = f"User_{session_id[:8]}" if session_id != "anonymous" else "Анонимный пользователь"

    # Get unlocked achievements count
    achievements = [
        progress.topics_read >= 1,
        progress.topics_read >= 5,
        progress.topics_read >= 10,
        progress.quizzes_passed >= 1,
        progress.quizzes_passed >= 5,
        progress.total_score >= 100
    ]
    unlocked_count = sum(achievements)

    # Get recent quiz results
    recent_results = db.query(QuizResult).order_by(QuizResult.completed_at.desc()).limit(5).all() if progress else []

    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # center
    )
    story.append(Paragraph("Отчет о прогрессе обучения", title_style))
    story.append(Spacer(1, 20))

    # User info
    story.append(Paragraph(f"<b>Пользователь:</b> {username}", styles['Normal']))
    story.append(Paragraph(f"<b>Дата отчета:</b> {datetime.now(UTC).strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Progress metrics
    story.append(Paragraph("<b>Основные показатели:</b>", styles['Heading2']))
    progress_data_list = [
        ["Показатель", "Значение"],
        ["Прочитано тем", str(progress_data["topics_read"])],
        ["Сдано тестов", str(progress_data["quizzes_passed"])],
        ["Общий балл", str(progress_data["total_score"])],
        ["Уровень", str(progress_data["level"])],
        ["Опыт (XP)", str(progress_data["experience"])],
        ["Разблокировано достижений", f"{unlocked_count}/6"]
    ]

    progress_table = Table(progress_data_list, colWidths=[200, 100])
    progress_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(progress_table)
    story.append(Spacer(1, 20))

    # Recent quiz results
    if recent_results:
        story.append(Paragraph("<b>Последние результаты тестов:</b>", styles['Heading2']))
        quiz_data = [["Тест", "Балл", "Максимум", "Процент", "Дата"]]
        for result in recent_results:
            percentage = (result.score / result.total * 100) if result.total > 0 else 0
            quiz_data.append([
                f"Тест #{result.quiz_id}",
                str(result.score),
                str(result.total),
                f"{percentage:.1f}%",
                result.completed_at.strftime("%d.%m.%Y") if result.completed_at else "Не указано"
            ])

        quiz_table = Table(quiz_data, colWidths=[100, 60, 60, 60, 80])
        quiz_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(quiz_table)
    else:
        story.append(Paragraph("<i>Нет данных о результатах тестов</i>", styles['Normal']))

    story.append(Spacer(1, 20))

    # Footer
    story.append(Paragraph("Отчет создан с использованием платформы TestLearn", styles['Italic']))
    story.append(Paragraph("© 2026 TestLearn. Все права защищены.", styles['Italic']))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    # Return PDF as response
    from fastapi.responses import StreamingResponse
    timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
    return StreamingResponse(
        io.BytesIO(buffer.read()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=progress_report_{timestamp}.pdf"}
    )
