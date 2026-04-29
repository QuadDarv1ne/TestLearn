# TestLearn — Educational Platform for Software Testing Fundamentals

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)

An educational web platform for learning the basics of software testing, designed as a course project for the "Databases" discipline at MFUA.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

## Overview

TestLearn is an interactive learning platform that helps users understand fundamental concepts of software testing through structured theory, practical quizzes, and a comprehensive glossary of terms. The platform implements a session-based progress tracking system to monitor user advancement through the learning material.

### Key Characteristics
- **Educational Focus**: Comprehensive coverage of software testing fundamentals
- **Interactive Learning**: Theory combined with self-assessment quizzes
- **Progress Tracking**: Session-based monitoring of topics read and quiz performance
- **Responsive Design**: Works on desktop and mobile devices
- **Open Source**: MIT licensed for educational and commercial use

## Features

### Learning Modules
- 📚 **Structured Theory**: 16 topics organized into 5 testing categories
- 🔍 **Smart Search**: Full-text search across theory and glossary
- 📖 **Glossary**: 43 essential testing terms with alphabetical filtering
- 🏆 **Progress Tracking**: Monitor completed topics and quiz scores
- 🔖 **Bookmarking**: Save important topics for quick reference

### Assessment Tools
- 📝 **Interactive Quizzes**: 6 tests with 50+ questions total
- ⏱️ **Timed Sessions**: Optional timer for quiz realism
- 🔄 **Question Randomization**: Different question order each attempt
- 💡 **Detailed Explanations**: Learn from correct and incorrect answers
- 📊 **Results Analytics**: View performance history and export to CSV

### Technical Implementation
- ⚡ **FastAPI Backend**: High-performance Python framework
- 🗃️ **SQLite Database**: Lightweight, zero-configuration storage
- 🎨 **Tailwind CSS**: Modern utility-first styling (via CDN)
- 🔧 **Jinja2 Templating**: Clean separation of presentation and logic
- 📱 **Responsive Layout**: Mobile-friendly design without frameworks

## Project Structure

```
testlearn/
├── main.py                 # Application entry point and API logic
├── requirements.txt        # Python dependencies
├── testlearn.db            # SQLite database (auto-generated)
├── .gitignore              # Git exclusion rules
├── todo.md                 # Development notes and roadmap
├── README.md               # This file (English)
└── README_RU.md            # Russian documentation
├── app/                    # Python package
│   └── __init__.py         # Package initializer
├── static/                 # Static assets (CSS, JS, images)
│   └── .gitkeep            # Placeholder for empty directory
└── templates/              # Jinja2 HTML templates
    ├── base.html           # Base layout with navigation and footer
    ├── index.html          # Landing page
    ├── theory.html         # Topic listing and search
    ├── topic.html          # Individual topic display
    ├── quiz_list.html      # Available quizzes overview
    ├── quiz.html           # Interactive quiz taking
    ├── quiz_result.html    # Quiz results and explanations
    ├── glossary.html       # Term dictionary with search
    ├── stats.html          # Progress analytics and export
    ├── database.html       # DB schema visualization (Mermaid)
    ├── feedback.html       # User feedback submission and history
    ├── about.html          # Project information page
    ├── 404.html            # Not found page
    └── bookmarks.html      # Saved topics management
    └── admin/              # Administrative interface
        ├── base.html       # Admin layout
        ├── categories.html # Category management
        ├── topics.html     # Topic management
        ├── questions.html  # Question management
        └── glossary.html   # Glossary term management
```

## Database Design

The platform uses SQLite with 8 interconnected tables following normalization principles:

### Core Tables
1. **categories** - Testing types (functional, non-functional, methodologies, etc.)
2. **topics** - Educational content items linked to categories
3. **quizzes** - Assessment collections (optionally linked to categories)
4. **questions** - Quiz items with multiple choice answers
5. **quiz_results** - User attempt records with scoring
6. **glossary** - Terminology reference with alphabetical categorization
7. **feedback** - User-submitted comments and ratings
8. **user_progress** - Session-based learning tracking
9. **read_topics** - Many-to-many: sessions ↔ topics (reading progress)
10. **bookmarks** - Many-to-many: sessions ↔ topics (user bookmarks)

### Entity Relationship Diagram
View the complete database schema in the application at `/database` or see `templates/database.html` for the Mermaid.js diagram.

## API Endpoints

TestLearn provides a comprehensive RESTful API for programmatic access. API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### Authentication & Authorization

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | User login with username/password |
| `/api/auth/register` | POST | Register new user |
| `/api/auth/logout` | POST | User logout |
| `/api/auth/me` | GET | Get current user info |

### Categories & Topics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/categories` | GET | List all categories (with pagination) |
| `/api/categories/{id}` | GET | Get single category details |
| `/api/topics` | GET | List all topics (filterable by category) |
| `/api/topics/{id}` | GET | Get single topic with content |
| `/api/topics/{id}/bookmarks` | POST | Bookmark a topic |

### Quizzes & Questions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/quizzes` | GET | List all available quizzes |
| `/api/quizzes/{id}` | GET | Get quiz details |
| `/api/quizzes/{id}/questions` | GET | Get quiz questions (without answers) |
| `/api/quizzes/{id}/submit` | POST | Submit quiz answers |

### Glossary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/glossary` | GET | List all glossary terms (filterable by letter) |
| `/api/glossary/{id}` | GET | Get single term definition |

### Progress & Statistics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Platform-wide statistics |
| `/api/progress` | GET | Get user progress |
| `/api/progress/xp` | POST | Add experience points |
| `/api/stats/export/pdf` | GET | Export progress as PDF report |
| `/api/stats/export/csv` | GET | Export quiz results as CSV |

### Gamification

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/leaderboard` | GET | Get top users by experience |
| `/api/achievements` | GET | Get user achievements |
| `/api/daily-challenge` | GET | Get daily challenge |

### Social Features

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/comments/{topic_id}` | GET | Get comments for a topic |
| `/api/comments` | POST | Add a comment |
| `/api/comments/{id}/like` | POST | Like a comment |
| `/api/notifications` | GET | Get user notifications |
| `/api/notifications/{id}/read` | POST | Mark notification as read |

### Feedback

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/feedback` | GET | List recent feedback |
| `/api/feedback` | POST | Submit feedback |

### Search

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | GET | Full-text search across topics and glossary |

### Health Checks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Basic health check |
| `/api/health/detailed` | GET | Detailed health check with DB status |
| `/api/ready` | GET | Readiness check for Kubernetes |
| `/api/live` | GET | Liveness check for Kubernetes |
| `/api/info` | GET | Application version and info |

## Getting Started

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (optional, for cloning)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/QuadDarv1ne/TestLearn.git
   cd TestLearn
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Activate the environment:
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Direct Execution
```bash
# Start the development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Open in browser
http://localhost:8000
```

#### Using Docker
```bash
# Build and run with Docker Compose (recommended)
docker-compose up --build

# The application will be available at http://localhost:8000

# To run in detached mode:
docker-compose up -d

# To stop and remove containers:
docker-compose down
```

#### Manual Docker Usage
```bash
# Build the Docker image
docker build -t testlearn .

# Run the container
docker run -p 8000:8000 -v $(pwd)/testlearn.db:/app/testlearn.db testlearn
```

For production deployment, consider using a proper ASGI server like Hypercorn or Uvicorn workers behind a reverse proxy.

## Usage

### Navigating the Platform
1. **Home Page**: Start at the landing page to get an overview
2. **Theory Section**: Browse or search through learning topics by category
3. **Topics**: Click on any topic to read detailed content with examples
4. **Quizzes**: Test your knowledge in the quiz section
5. **Glossary**: Look up testing terminology anytime
6. **Stats**: Review your learning progress and export results
7. **Feedback**: Share your thoughts to help improve the platform

### Administrative Features
Access the admin panel by navigating to `/admin` (note: currently lacks authentication - for educational purposes only):
- Manage categories, topics, questions, and glossary terms
- View system statistics and user feedback

## Contributing

We welcome contributions to improve TestLearn! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow the existing code style and conventions
- Write clear, descriptive commit messages
- Update documentation as needed
- Ensure new features include appropriate tests
- Keep pull requests focused on a single improvement

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (to be added).

## Contact

**Project Author**: Самойлов Д.А. (D.A. Samoilov)  
**Institution**: Московский областной филиал МФЮА (Moscow Oblast Branch of MFUA)  
**Direction**: 09.03.03 Прикладная информатика (Applied Informatics)  

For questions or suggestions, please open an issue in the GitHub repository.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [SQLite](https://www.sqlite.org/) - Embedded database engine
- [Jinja2](https://palletsprojects.com/p/jinja/) - Python templating engine
- [Mermaid.js](https://mermaid.js.org/) - Diagram generation for documentation
- All contributors and testers who helped improve the platform

## Recent Improvements (v2.0.0)

### New Features
- ✅ **Health Check Endpoints**: `/api/health`, `/api/ready`, `/api/live` for monitoring
- ✅ **Enhanced Error Handling**: Global exception handlers with proper logging
- ✅ **Dark/Light Theme**: Toggle between light and dark modes
- ✅ **Advanced Search**: Real-time search with highlighting and recent searches
- ✅ **Quiz Timer**: Countdown timer with visual warnings
- ✅ **Toast Notifications**: User-friendly feedback messages
- ✅ **API Documentation**: Swagger UI at `/api/docs` and ReDoc at `/api/redoc`

### Docker Improvements
- ✅ **Multi-stage builds**: Optimized production images
- ✅ **Health checks**: Container health monitoring
- ✅ **Development profile**: Hot reload support
- ✅ **Test profile**: Run tests in isolated container

### Development Tools
- ✅ **Makefile**: Simplified commands for common tasks
- ✅ **Environment configuration**: `.env.example` for easy setup
- ✅ **Comprehensive tests**: 50+ test cases covering all endpoints

### JavaScript Modules
- ✅ `base.js`: Common utilities (Toast, Loading, Storage, API)
- ✅ `theme.js`: Theme management and toggle
- ✅ `search.js`: Advanced search functionality
- ✅ `quiz.js`: Quiz timer and navigation
- ✅ `gamification.js`: Levels, achievements, daily challenges
- ✅ `social.js`: Comments, notifications, leaderboard