# EventScheduler

A production-ready event management platform built with Flask, featuring AI-powered natural language event creation through OpenAI integration.

## Architecture Overview

EventScheduler follows a modular Flask application architecture with clear separation of concerns:

```
event_scheduler/
├── app.py                     # Application factory and configuration
├── models/                    # Data models and business logic
├── routes/                    # HTTP route handlers (Blueprint-based)
├── services/                  # Business logic and external integrations
├── templates/                 # Jinja2 template engine views
├── static/                    # Client-side assets (CSS, JS, images)
└── data/                      # SQLite database storage
```

## Core Features

### Event Management System
- **Full CRUD Operations**: Create, read, update, and delete events with comprehensive data validation
- **Status Tracking**: Multi-state event management (upcoming, attending, maybe, declined)
- **Temporal Intelligence**: Advanced date/time handling with timezone awareness
- **Location Management**: Flexible location data with geocoding capabilities

### AI-Powered Natural Language Processing
- **Smart Event Creation**: Parse natural language input using OpenAI GPT-4o-mini
- **Contextual Understanding**: Intelligent extraction of dates, times, locations, and descriptions
- **Fallback Processing**: Robust keyword-based parsing when AI services are unavailable
- **Error Handling**: Graceful degradation with user-friendly clarification prompts

### Advanced Search & Filtering
- **Multi-criteria Search**: Full-text search across titles, descriptions, and locations
- **Temporal Filtering**: Date range queries with flexible time boundaries
- **Status Aggregation**: Filter and group events by status categories
- **Real-time Suggestions**: Dynamic search autocomplete with debounced queries

### Modern User Interface
- **Responsive Design**: Mobile-first approach with Bootstrap 5 framework
- **Progressive Enhancement**: Enhanced UX with subtle animations and micro-interactions
- **Accessibility Compliant**: WCAG 2.1 AA standards with semantic HTML and ARIA labels
- **Performance Optimized**: Lazy loading, efficient DOM manipulation, and optimized asset delivery

## Technology Stack

### Backend Infrastructure
- **Flask 3.0**: Modern Python web framework with blueprint architecture
- **SQLite**: Embedded database with ACID compliance
- **OpenAI API**: GPT-4o-mini integration for natural language processing
- **Python 3.8+**: Leveraging modern Python features and type hints

### Frontend Technologies
- **Bootstrap 5**: Component-based UI framework with utility classes
- **Vanilla JavaScript**: ES6+ features for enhanced interactivity
- **CSS3**: Custom properties, Grid, Flexbox, and animations
- **Jinja2**: Server-side templating with template inheritance

### Development Tools
- **python-dotenv**: Environment configuration management
- **Flask Blueprints**: Modular route organization
- **SQLite3**: Direct database operations for optimal performance

## Installation & Configuration

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (optional - application gracefully degrades without it)

### Environment Setup

1. **Clone and navigate to project directory**
   ```bash
   git clone <repository-url>
   cd event_scheduler
   ```

2. **Create isolated Python environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize and run application**
   ```bash
   python app.py
   ```

### Environment Configuration

```bash
# Flask Configuration
SECRET_KEY=your-cryptographically-secure-secret-key
FLASK_ENV=development
FLASK_DEBUG=True

# OpenAI Integration (Optional)
OPENAI_API_KEY=sk-your-openai-api-key

# Database Configuration
DATABASE_URL=sqlite:///data/events.db
```

## API Documentation

### Event Management Endpoints

#### Create Event
```http
POST /events/add
Content-Type: application/x-www-form-urlencoded

title=Team Meeting&date=2024-06-25T14:00&location=Conference Room A
```

#### Natural Language Event Creation
```http
POST /events/add
Content-Type: application/x-www-form-urlencoded

ai_input=Team meeting tomorrow at 3pm in conference room A
```

#### Retrieve Event
```http
GET /events/api/{event_id}
```

#### Update Event
```http
POST /events/edit/{event_id}
Content-Type: application/x-www-form-urlencoded
```

#### Delete Event
```http
POST /events/delete/{event_id}
```

### Search & Filter Endpoints

#### Advanced Search
```http
GET /search/?q={query}&type={search_type}&status={status}&date_from={start}&date_to={end}
```

#### Quick Search API
```http
GET /search/api/quick-search?q={query}&limit={limit}
```

#### Search Suggestions
```http
GET /search/api/suggestions?q={partial_query}
```

## Natural Language Processing

### Supported Input Patterns

The AI service intelligently parses various natural language constructs:

**Temporal Expressions**
- Relative dates: "tomorrow", "next week", "next Monday"
- Specific times: "at 3pm", "at 14:30", "at noon"
- Date combinations: "Friday at 2pm", "next Tuesday morning"

**Location Extraction**
- Preposition-based: "meeting in conference room", "lunch at cafe"
- Context-aware: Distinguishes between time and location references

**Event Classification**
- Automatic status assignment based on context
- Intelligent description generation
- Title extraction from complex input

### Fallback Processing

When OpenAI services are unavailable, the system employs sophisticated keyword-based parsing:

```python
# Example: "Team meeting tomorrow at 3pm in conference room"
{
    "title": "Team meeting",
    "date": "2024-06-25T15:00:00",
    "location": "conference room",
    "status": "upcoming"
}
```

## Performance Considerations

### Database Optimization
- Indexed queries for efficient search operations
- Connection pooling for concurrent request handling
- Prepared statements for SQL injection prevention

### Frontend Optimization
- Debounced search queries to reduce server load
- Local storage for user preferences
- Lazy loading of non-critical resources
- Optimized CSS with minimal render-blocking

### Caching Strategy
- Template caching for repeated renders
- Static asset versioning for cache busting
- Client-side caching for API responses

## Security Implementation

### Data Protection
- Input sanitization and validation
- SQL injection prevention through parameterized queries
- XSS protection via template escaping
- CSRF protection with secure tokens

### API Security
- Rate limiting on sensitive endpoints
- Secure API key management
- Environment-based configuration isolation

### Client-Side Security
- Content Security Policy headers
- Secure cookie configuration
- HTTPS enforcement in production

## Deployment Architecture

### Production Deployment

```bash
# Production WSGI server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment-Specific Configuration

```python
# Production settings
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    # Additional production configurations
```

### Database Migration Strategy

For production deployments requiring PostgreSQL:

```python
# Alternative database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/eventdb')
```

## Testing Strategy

### Unit Testing Framework
```bash
# Install testing dependencies
pip install pytest pytest-flask

# Run test suite
pytest tests/
```

### Integration Testing
- End-to-end workflow testing
- API endpoint validation
- Database transaction testing

### Performance Testing
- Load testing with simulated concurrent users
- Database query performance analysis
- Frontend rendering optimization validation

## Contributing Guidelines

### Development Workflow
1. Fork repository and create feature branch
2. Implement changes with comprehensive testing
3. Ensure code style compliance (PEP 8)
4. Submit pull request with detailed description

### Code Quality Standards
- Type hints for function signatures
- Comprehensive docstrings for modules and functions
- Error handling with appropriate exception types
- Logging implementation for debugging and monitoring

## Troubleshooting

### Common Issues

**OpenAI API Connection Errors**
```python
# Verify API key configuration
print(os.getenv('OPENAI_API_KEY'))
```

**Database Connectivity Issues**
```bash
# Reset database
rm data/events.db
python app.py
```

**Frontend Asset Loading**
```bash
# Clear browser cache
Ctrl + F5 (Windows/Linux)
Cmd + Shift + R (macOS)
```

## License & Attribution

This project demonstrates modern Flask application development practices and serves as a comprehensive example of integrating AI services with traditional web applications.

**Built with:**
- Flask ecosystem and Python community tools
- OpenAI GPT-4o-mini for natural language processing
- Bootstrap framework for responsive design
- Modern web standards and accessibility guidelines

---

*EventScheduler - Intelligent event management for the modern workflow*