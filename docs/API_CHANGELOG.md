# API Changelog

All notable changes to the TestLearn API are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.10] - 2026-05-02

### Added
- Comprehensive API examples in README.md for all major endpoints
- Documentation for authentication, categories, topics, quizzes, progress, gamification, social features, search, feedback, and export endpoints

### Changed
- Enhanced API documentation with practical curl examples

## [2.3.9] - 2026-05-02

### Added
- Test for successful admin login
- 90/90 tests passing (100%)

## [2.3.8] - 2026-05-02

### Added
- Integration tests for auth registration (4 new tests)
- 89/89 tests passing (100%)

### Changed
- Replaced password hashing algorithm from bcrypt to SHA-256 with salt
- Fixed datetime.utcnow() deprecation warning

## [2.3.7] - 2026-05-02

### Changed
- Fixed Jinja2Templates deprecation warning (removed auto_reload)
- 85/85 tests passing (100%)

## [2.3.6] - 2026-05-02

### Added
- Created `dev` branch for development workflow (dev → main)
- 85/85 tests passing (100%)

## [2.3.3] - 2026-05-02

### Changed
- Fixed pytest warnings: added `asyncio_mode = auto` and `asyncio_default_fixture_loop_scope = function`
- 85/85 tests passing (100%)

## [2.3.2] - 2026-05-02

### Added
- Tests for CertificateService (7 tests covering certificate generation)
- 85/85 tests passing (100%)

## [2.3.1] - 2026-05-02

### Fixed
- Bug in quiz_checker_service.py: field `case_sensitive` renamed to `answer_case_sensitive`

### Added
- Tests for QuizCheckerService (19 tests covering all question types)
- 78/78 tests passing (100%)

## [2.3.0] - 2026-05-02

### Added
- CSRF protection middleware for forms (`app/middleware/csrf.py`)
- Enhanced feedback validation (name, email, message, rating)
- Pagination for leaderboard, comments, and notifications
- 59/59 tests passing (100%)

### Changed
- Fixed alembic.ini format (removed docstring)
- Adapted tests for new paginated response format

## [2.2.0] - 2026-05-02

### Added
- Database indexes for performance:
  - `quiz_id`, `session_id`, `created_at` in QuizResult
  - `topic_id`, `user_id`, `created_at` in Comment
- Created `app/db/__init__.py` with model exports
- Created `data/` and `logs/` directories for Docker volumes
- 59/59 tests passing (100%)

### Changed
- Refactored `seed_initial_data` moved to `progress_service.py`
- Updated `.gitignore` to include `data/` and `logs/`

## [2.2.0] - 2026-04-30

### Added
- Extended question database: 85 questions across 5 quizzes (25+15+15+15+15)
- Diverse question types: single choice, multiple choice, true/false, short answer, matching, ordering, fill blank
- Comprehensive coverage: functional/non-functional testing, methodologies (TDD/BDD/ATDD), tools (Selenium/Postman/JUnit)
- Modular service architecture: `progress_service.py`, `gamification_service.py`, `social_service.py`, `search_service.py`
- Alembic migrations configured (initial migration)
- Social endpoints tests: comments, likes, notifications
- Gamification endpoints tests: leaderboard, achievements, certificates
- 78/78 tests passing (100%)
- Enhanced navigation: multi-level menu with dropdown for desktop, burger menu with accordion for mobile
- Individual topic page with navigation (prev/next) and progress tracking
- User registration with validation
- Password recovery page
- User model with correct relationships for achievements
- QuizCheckerService for automated question quality control
- CertificateService for PDF certificate generation
- Docker Compose profiles: dev, test, production separated

### Fixed
- Bug in auth.py (Response with dict content)

## [2.1.0] - 2026-04-29

### Added
- Rate Limiting with slowapi (100 requests/min default)
- In-memory caching for statistics
- SQL query optimization with indexes

### Changed
- Improved error handling and logging

## [2.0.0] - 2026-04-27

### Added
- Gamification system:
  - Levels (1-50) with XP progression
  - 10+ achievements
  - Leaderboard with pagination
  - Daily challenges
- Social features:
  - Comments with pagination
  - Comment likes
  - User notifications
  - Certificate generation
- Theme support: light/dark mode
- Advanced search with highlighting
- Quiz timer with visual warnings
- Toast notifications
- Swagger UI and ReDoc API documentation

### Changed
- Multi-stage Docker builds for optimized images
- Container health checks
- Development profile with hot reload
- Test profile for isolated container testing

## [1.0.0] - 2026-04-26

### Added
- Initial release with core features:
  - 5 testing categories with 16 topics
  - 5 quizzes with 85 questions
  - Glossary (43 terms)
  - Progress tracking (sessions)
  - Topic bookmarks
  - Feedback with rating
  - SQLite database with 8 tables
  - RESTful API endpoints
  - Jinja2 templates with Tailwind CSS
  - Responsive design

---

## API Endpoint Changes

### Authentication
- **2.3.0**: Added CSRF protection for login/register forms
- **2.2.0**: Changed password hashing from bcrypt to SHA-256

### Categories & Topics
- **2.3.0**: Added pagination support
- **2.2.0**: Enhanced topic navigation with prev/next

### Quizzes
- **2.3.1**: Fixed answer validation field name
- **2.2.0**: Added 7 new question types support

### Gamification
- **2.3.0**: Added pagination to leaderboard
- **2.2.0**: Added CertificateService for PDF generation

### Social
- **2.3.0**: Added pagination to comments and notifications
- **2.2.0**: Complete social features implementation

### Search
- **2.1.0**: Added full-text search with highlighting

---

## Breaking Changes

### Version 2.3.0
- Feedback response format changed to include pagination
- Leaderboard response format changed to include pagination
- Comments response format changed to include pagination

### Version 2.2.0
- Password hashing algorithm changed from bcrypt to SHA-256
- All users must reset passwords after upgrade

---

## Deprecations

### Version 2.3.7
- Removed: Jinja2Templates `auto_reload` parameter (deprecated)

### Version 2.3.8
- Removed: `datetime.utcnow()` (deprecated in Python 3.12+)
- Replaced with: `datetime.now(timezone.utc)`

---

## Migration Guide

### Upgrading to 2.3.0
1. Update dependencies: `pip install -r requirements.txt`
2. Run database migrations: `alembic upgrade head`
3. Update API clients to handle paginated responses

### Upgrading to 2.2.0
1. Backup your database
2. Update dependencies: `pip install -r requirements.txt`
3. Run database migrations: `alembic upgrade head`
4. Users must reset passwords (hashing algorithm changed)

---

## Support

For API questions or issues:
- Open an issue on GitHub
- Check Swagger UI at `/api/docs`
- Check ReDoc at `/api/redoc`
