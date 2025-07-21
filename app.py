from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
import re
import os
import csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database configuration
DATABASE = 'data_collection.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the required tables"""
    conn = get_db_connection()
    
    # Create contacts table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create notes table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            note_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def validate_email(email):
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format (allows various formats)"""
    # Remove all non-digit characters for validation
    digits_only = re.sub(r'[^\d]', '', phone)
    # Check if it's a valid length (10-15 digits)
    return len(digits_only) >= 10 and len(digits_only) <= 15

@app.route('/')
def index():
    """Display the data collection form"""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_data():
    """Handle form submission"""
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # Validation
    errors = []
    
    if not first_name:
        errors.append('First name is required')
    
    if not last_name:
        errors.append('Last name is required')
    
    if not email:
        errors.append('Email is required')
    elif not validate_email(email):
        errors.append('Please enter a valid email address')
    
    if not phone:
        errors.append('Phone number is required')
    elif not validate_phone(phone):
        errors.append('Please enter a valid phone number (10-15 digits)')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template('index.html', 
                             first_name=first_name, 
                             last_name=last_name, 
                             email=email, 
                             phone=phone)
    
    # Save to database
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO contacts (first_name, last_name, email, phone)
            VALUES (?, ?, ?, ?)
        ''', (first_name, last_name, email, phone))
        conn.commit()
        conn.close()
        
        flash('Data saved successfully!', 'success')
        return redirect(url_for('success'))
    
    except Exception as e:
        flash(f'Error saving data: {str(e)}', 'error')
        return render_template('index.html', 
                             first_name=first_name, 
                             last_name=last_name, 
                             email=email, 
                             phone=phone)

@app.route('/success')
def success():
    """Display success page"""
    return render_template('success.html')

@app.route('/view')
def view_data():
    """View all collected data"""
    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('view.html', contacts=contacts)

@app.route('/export_csv')
def export_csv():
    """Export all data as CSV file"""
    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY created_at DESC').fetchall()
    conn.close()
    
    # Create CSV content
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Date Added'])
    
    # Write data rows
    for contact in contacts:
        writer.writerow([
            contact['id'],
            contact['first_name'],
            contact['last_name'],
            contact['email'],
            contact['phone'],
            contact['created_at']
        ])
    
    # Prepare response
    csv_data = output.getvalue()
    output.close()
    
    # Create filename with current date
    from datetime import datetime
    filename = f"contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Return CSV as downloadable file
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )

@app.route('/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    """Delete a specific contact by ID"""
    try:
        conn = get_db_connection()
        
        # Check if contact exists
        contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
        if not contact:
            flash('Contact not found', 'error')
            conn.close()
            return redirect(url_for('view_data'))
        
        # Delete the contact
        conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        conn.commit()
        conn.close()
        
        flash(f'Contact "{contact["first_name"]} {contact["last_name"]}" has been deleted successfully', 'success')
        
    except Exception as e:
        flash(f'Error deleting contact: {str(e)}', 'error')
    
    return redirect(url_for('view_data'))

@app.route('/help')
def help_page():
    """Display help and instructions page"""
    return render_template('help.html')

@app.route('/admin')
def admin_page():
    """Display admin page with raw database contents"""
    conn = get_db_connection()
    
    # Get all contacts
    contacts = conn.execute('SELECT * FROM contacts ORDER BY id').fetchall()
    
    # Get all notes
    notes = conn.execute('''
        SELECT n.*, c.first_name, c.last_name 
        FROM notes n 
        LEFT JOIN contacts c ON n.contact_id = c.id 
        ORDER BY n.id
    ''').fetchall()
    
    # Get table structure information
    contacts_schema = conn.execute('PRAGMA table_info(contacts)').fetchall()
    notes_schema = conn.execute('PRAGMA table_info(notes)').fetchall()
    
    # Get database statistics
    contacts_count = conn.execute('SELECT COUNT(*) as count FROM contacts').fetchone()['count']
    notes_count = conn.execute('SELECT COUNT(*) as count FROM notes').fetchone()['count']
    
    conn.close()
    
    return render_template('admin.html', 
                         contacts=contacts, 
                         notes=notes,
                         contacts_schema=contacts_schema,
                         notes_schema=notes_schema,
                         contacts_count=contacts_count,
                         notes_count=notes_count)

@app.route('/contact/<int:contact_id>/notes')
def view_contact_notes(contact_id):
    """View all notes for a specific contact"""
    conn = get_db_connection()
    
    # Get contact details
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    if not contact:
        flash('Contact not found', 'error')
        conn.close()
        return redirect(url_for('view_data'))
    
    # Get all notes for this contact
    notes = conn.execute('''
        SELECT * FROM notes 
        WHERE contact_id = ? 
        ORDER BY created_at DESC
    ''', (contact_id,)).fetchall()
    
    conn.close()
    return render_template('contact_notes.html', contact=contact, notes=notes)

@app.route('/contact/<int:contact_id>/notes/add', methods=['GET', 'POST'])
def add_note(contact_id):
    """Add a new note to a contact"""
    conn = get_db_connection()
    
    # Verify contact exists
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    if not contact:
        flash('Contact not found', 'error')
        conn.close()
        return redirect(url_for('view_data'))
    
    if request.method == 'POST':
        note_text = request.form.get('note_text', '').strip()
        
        if not note_text:
            flash('Note text is required', 'error')
            conn.close()
            return render_template('add_edit_note.html', contact=contact, note_text=note_text)
        
        try:
            conn.execute('''
                INSERT INTO notes (contact_id, note_text)
                VALUES (?, ?)
            ''', (contact_id, note_text))
            conn.commit()
            conn.close()
            
            flash('Note added successfully!', 'success')
            return redirect(url_for('view_contact_notes', contact_id=contact_id))
        
        except Exception as e:
            flash(f'Error adding note: {str(e)}', 'error')
            conn.close()
            return render_template('add_edit_note.html', contact=contact, note_text=note_text)
    
    conn.close()
    return render_template('add_edit_note.html', contact=contact)

@app.route('/contact/<int:contact_id>/notes/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(contact_id, note_id):
    """Edit an existing note"""
    conn = get_db_connection()
    
    # Verify contact and note exist
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    note = conn.execute('SELECT * FROM notes WHERE id = ? AND contact_id = ?', (note_id, contact_id)).fetchone()
    
    if not contact or not note:
        flash('Contact or note not found', 'error')
        conn.close()
        return redirect(url_for('view_data'))
    
    if request.method == 'POST':
        note_text = request.form.get('note_text', '').strip()
        
        if not note_text:
            flash('Note text is required', 'error')
            conn.close()
            return render_template('add_edit_note.html', contact=contact, note=note, note_text=note_text)
        
        try:
            conn.execute('''
                UPDATE notes 
                SET note_text = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (note_text, note_id))
            conn.commit()
            conn.close()
            
            flash('Note updated successfully!', 'success')
            return redirect(url_for('view_contact_notes', contact_id=contact_id))
        
        except Exception as e:
            flash(f'Error updating note: {str(e)}', 'error')
            conn.close()
            return render_template('add_edit_note.html', contact=contact, note=note, note_text=note_text)
    
    conn.close()
    return render_template('add_edit_note.html', contact=contact, note=note)

@app.route('/contact/<int:contact_id>/notes/<int:note_id>/delete', methods=['POST'])
def delete_note(contact_id, note_id):
    """Delete a specific note"""
    try:
        conn = get_db_connection()
        
        # Check if note exists and belongs to the contact
        note = conn.execute('SELECT * FROM notes WHERE id = ? AND contact_id = ?', (note_id, contact_id)).fetchone()
        if not note:
            flash('Note not found', 'error')
            conn.close()
            return redirect(url_for('view_contact_notes', contact_id=contact_id))
        
        # Delete the note
        conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()
        
        flash('Note deleted successfully', 'success')
        
    except Exception as e:
        flash(f'Error deleting note: {str(e)}', 'error')
    
    return redirect(url_for('view_contact_notes', contact_id=contact_id))

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
