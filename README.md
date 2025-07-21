# Data Collection App

A Python Flask web application for collecting and storing user data with validation.

## Features

- **Web Form Interface**: Clean, responsive form for data entry
- **SQLite Database**: Lightweight database for data storage
- **Input Validation**: 
  - Email format validation
  - Phone number validation (10-15 digits)
  - Required field validation
- **Data Viewing**: View all collected entries in a table format
- **Notes Management**: Add, edit, and delete notes for each contact with timestamps
- **Record Management**: Delete individual records with confirmation prompts
- **CSV Export**: Download all data as a CSV file with timestamped filename
- **Admin Panel**: View raw database contents and schema information for debugging
- **Help System**: Comprehensive help page with usage instructions and troubleshooting
- **Modern UI**: Beautiful, responsive design with gradient styling

## Database Schema

The application stores the following data:

### Contacts Table
- `id` (INTEGER, PRIMARY KEY, AUTO INCREMENT)
- `first_name` (TEXT, NOT NULL)
- `last_name` (TEXT, NOT NULL)
- `email` (TEXT, NOT NULL, validated)
- `phone` (TEXT, NOT NULL, validated)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

### Notes Table
- `id` (INTEGER, PRIMARY KEY, AUTO INCREMENT)
- `contact_id` (INTEGER, FOREIGN KEY to contacts.id)
- `note_text` (TEXT, NOT NULL)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

## Installation

1. Ensure Python 3.6+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Submit Data**: Fill out the form on the homepage and click "Submit Data"
2. **View Data**: Click "View Collected Data" to see all entries
3. **Manage Notes**: Click "📝 Notes" next to any contact to add, edit, or delete notes
4. **Delete Records**: Click the "Delete" button next to any record (with confirmation)
5. **Export Data**: Click "Export as CSV" to download all data as a spreadsheet file
6. **Admin Access**: Click "🔧 Admin Panel" to view raw database contents and schema
7. **Get Help**: Click "Help & Instructions" for detailed usage guidance
8. **Validation**: The app validates email format and phone numbers automatically

## Project Structure

```
GHCopilotDataCollectionApp/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── data_collection.db     # SQLite database (created automatically)
├── templates/
│   ├── index.html        # Main form page
│   ├── success.html      # Success confirmation page
│   ├── view.html         # Data viewing page
│   ├── help.html         # Help and instructions page
│   ├── contact_notes.html # Notes viewing page
│   ├── add_edit_note.html # Add/edit note form
│   └── admin.html        # Admin panel for raw database access
└── README.md             # This file
```

## Development

The application runs in debug mode by default, which provides:
- Auto-reload on file changes
- Detailed error messages
- Development server on all interfaces (0.0.0.0:5000)

## Security Notes

- Change the `secret_key` in `app.py` for production use
- Consider adding CSRF protection for production
- Implement proper authentication for the data viewing feature in production
