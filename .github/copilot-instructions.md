<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Data Collection App - Copilot Instructions

This is a Python Flask web application for collecting user data with the following characteristics:

## Project Context
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with built-in Python sqlite3 module
- **Frontend**: HTML templates with embedded CSS
- **Validation**: Server-side validation for email and phone formats
- **Schema**: FirstName, LastName, Email (validated), Phone (validated)

## Code Style Preferences
- Use Python 3.6+ syntax and features
- Follow PEP 8 style guidelines
- Use descriptive variable names
- Include docstrings for functions
- Use Flask best practices for routing and templating

## Architecture Notes
- Single-file Flask application (`app.py`)
- Templates stored in `templates/` directory
- Database initialization happens on app startup
- Form validation occurs server-side with flash messages
- Responsive design with modern CSS styling

## Common Tasks
- When adding new fields, update both the database schema and HTML forms
- Validation functions should be separate and reusable
- Use Flask's `flash()` for user feedback messages
- Maintain consistent styling across all templates
