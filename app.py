import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, session, redirect, url_for, render_template
import pymysql

# App initialization
app = Flask(__name__)
app.secret_key = 'Lq991027!!'

# Correct path setup
base_dir = os.path.abspath(os.path.dirname(__file__))  # Get the current script's directory
log_dir = os.path.join(base_dir, 'logs')  # Logs directory
log_file_path = os.path.join(log_dir, 'app.log')  # Full log file path

# Debugging - print to confirm paths
print(f"Base directory: {base_dir}")
print(f"Log directory: {log_dir}")
print(f"Log file path: {log_file_path}")

# Ensure logs directory exists
if not os.path.exists(log_dir):
    print("Creating logs directory...")
    os.makedirs(log_dir)

# Rotating file handler setup
try:
    handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
except FileNotFoundError as e:
    print(f"Error occurred while setting up logging: {e}")
    raise

# Set up logging configuration
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.info("Flask application started successfully.")
  
# Import database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Lq991027!!',
    'database': 'urban_lab_db',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM Admins WHERE username = %s", (username,))
            admin = cursor.fetchone()

        if admin and admin['password_hash'] == password:
            session['admin_id'] = admin['id']
            logger.info(f"User {username} logged in successfully.") 
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")  
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/users', methods=['POST'])
def add_user_view():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    with db.cursor() as cursor:
        cursor.execute(
           """INSERT INTO Users (name, email, phone_number, user_type, organization) VALUES (%s, %s, %s, 
%s, %s)""",
            (name, email, data.get('phone_number'), data.get('user_type'), data.get('organization'))
        )
        db.commit()
    
    logger.info(f"User {name} ({email}) added by admin ID {session.get('admin_id')}") 
    return jsonify({"message": "User added successfully!"}), 201

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user_view(user_id):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
            db.commit()
            logger.info(f"User ID {user_id} deleted by admin ID {session.get('admin_id')}")   

            return jsonify({"message": "User deleted successfully!"})
        else:
            logger.warning(f"Attempted to delete non-existent user ID {user_id}") 
            return jsonify({"error": "User not found"}), 404


# Initialize database connection
def init_db():
    return pymysql.connect(**DB_CONFIG)

db = init_db()

# Test route
@app.route('/test', methods=['GET'])
def test_api():
    return jsonify({"message": "Flask app is running successfully!"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle admin login.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate admin credentials
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM Admins WHERE username = %s", (username,))
            admin = cursor.fetchone()

        if admin and admin['password_hash'] == password:  # Plain text comparison
            session['admin_id'] = admin['id']
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Log out the current admin.
    """
    session.pop('admin_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'admin_id' in session:
        with db.cursor() as cursor:
            # Fetch stats
            cursor.execute("SELECT COUNT(*) AS total_users FROM Users")
            total_users = cursor.fetchone()['total_users']
            cursor.execute("SELECT COUNT(*) AS total_interactions FROM Interactions")
            total_interactions = cursor.fetchone()['total_interactions']
            cursor.execute("SELECT COUNT(*) AS total_events FROM Events")
            total_events = cursor.fetchone()['total_events']

            # Fetch interaction types overview
            cursor.execute("""
                SELECT interaction_type AS type, COUNT(*) AS count
                FROM Interactions
                GROUP BY interaction_type
            """)
            interaction_types = cursor.fetchall()

        return render_template(
            'dashboard.html',
            total_users=total_users,
            total_interactions=total_interactions,
            total_events=total_events,
            interaction_types=interaction_types
        )
    return redirect(url_for('login'))

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Fetch statistics for the dashboard.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS user_count FROM Users")
        user_count = cursor.fetchone()['user_count']

        cursor.execute("SELECT COUNT(*) AS interaction_count FROM Interactions")
        interaction_count = cursor.fetchone()['interaction_count']

        cursor.execute("SELECT COUNT(*) AS event_count FROM Events")
        event_count = cursor.fetchone()['event_count']

    return jsonify({
        "user_count": user_count,
        "interaction_count": interaction_count,
        "event_count": event_count
    })


# API ROUTES FOR USERS
# ---------------------------

# Route to render the User Management page
@app.route('/users', methods=['GET'])
def users_page():
    """
    Render the user management page.
    """
    return render_template('users.html')

# API route to fetch all users
@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Fetch all users from the Users table.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
    return jsonify(users)

# API route to fetch a specific user by ID
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Fetch a user by their unique ID.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

# API route to add a new user
@app.route('/api/users', methods=['POST'])
def add_user_api():
    """
    Add a new user to the Users table.
    Requires: name, email, phone_number, user_type, and organization in the request body.
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    user_type = data.get('user_type')
    organization = data.get('organization')

    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO Users (name, email, phone_number, user_type, organization)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, email, phone_number, user_type, organization)
        )
        db.commit()
    return jsonify({"message": "User added successfully!"}), 201

# API route to update an existing user
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update an existing user's information.
    Requires: name, email, phone_number, user_type, and organization in the request body.
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    user_type = data.get('user_type')
    organization = data.get('organization')

    with db.cursor() as cursor:
        cursor.execute(
            """
            UPDATE Users
            SET name = %s, email = %s, phone_number = %s, user_type = %s, organization = %s
            WHERE id = %s
            """,
            (name, email, phone_number, user_type, organization, user_id)
        )
        db.commit()
    return jsonify({"message": "User updated successfully!"})

# API route to delete a user
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user_api(user_id):
    """
    Delete a user from the database.
    """
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
        db.commit()
    return jsonify({"message": "User deleted successfully!"})

# Interactions Management API

@app.route('/interactions', methods=['GET'])
def interactions_page():
    """
    Render the interactions management page.
    """
    return render_template('interactions.html')

# Route to get all interactions
@app.route('/interactions', methods=['GET'])
def get_interactions():
    """
    Fetch all interactions from the Interactions table.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Interactions")
        interactions = cursor.fetchall()
    return jsonify(interactions)

# Route to add a new interaction
@app.route('/interactions', methods=['POST'])
def add_interaction():
    """
    Add a new interaction to the Interactions table.
    Requires: user_id, interaction_type, details, and interaction_date in the request body.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    interaction_type = data.get('interaction_type')
    details = data.get('details')
    interaction_date = data.get('interaction_date')

    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO Interactions (user_id, interaction_type, details, interaction_date)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, interaction_type, details, interaction_date)
        )
        db.commit()
    return jsonify({"message": "Interaction added successfully!"}), 201

# Route to get a specific interaction by ID
@app.route('/interactions/<int:interaction_id>', methods=['GET'])
def get_interaction(interaction_id):
    """
    Fetch an interaction by its unique ID.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Interactions WHERE id = %s", (interaction_id,))
        interaction = cursor.fetchone()
    if interaction:
        return jsonify(interaction)
    else:
        return jsonify({"error": "Interaction not found"}), 404

# Route to update an interaction
@app.route('/interactions/<int:interaction_id>', methods=['PUT'])
def update_interaction(interaction_id):
    data = request.get_json()
    interaction_type = data.get('interaction_type')
    details = data.get('details')
    interaction_date = data.get('interaction_date')

    with db.cursor() as cursor:
        cursor.execute(
            """
            UPDATE Interactions
            SET interaction_type = %s, details = %s, interaction_date = %s
            WHERE id = %s
            """,
            (interaction_type, details, interaction_date, interaction_id)
        )
        db.commit()
    return jsonify({"message": "Interaction updated successfully!"})

# Route to delete an interaction
@app.route('/interactions/<int:interaction_id>', methods=['DELETE'])
def delete_interaction(interaction_id):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM Interactions WHERE id = %s", (interaction_id,))
        db.commit()
    return jsonify({"message": "Interaction deleted successfully!"})

# Events Management API

@app.route('/events', methods=['GET'])
def events_page():
    """
    Render the events management page.
    """
    return render_template('events.html')

# Route to get all events
@app.route('/events', methods=['GET'])
def get_events():
    """
    Fetch all events from the Events table.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Events")
        events = cursor.fetchall()
    return jsonify(events)

# Route to add a new event
@app.route('/events', methods=['POST'])
def add_event():
    """
    Add a new event to the Events table.
    Requires: name, description, event_date, location, and organizer_id in the request body.
    """
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    event_date = data.get('event_date')
    location = data.get('location')
    organizer_id = data.get('organizer_id')

    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO Events (name, description, event_date, location, organizer_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, description, event_date, location, organizer_id)
        )
        db.commit()
    return jsonify({"message": "Event added successfully!"}), 201

# Route to get a specific event by ID
@app.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """
    Fetch an event by its unique ID.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
    if event:
        return jsonify(event)
    else:
        return jsonify({"error": "Event not found"}), 404

# Route to update an event
@app.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    event_date = data.get('event_date')
    location = data.get('location')

    with db.cursor() as cursor:
        cursor.execute(
            """
            UPDATE Events
            SET name = %s, description = %s, event_date = %s, location = %s
            WHERE id = %s
            """,
            (name, description, event_date, location, event_id)
        )
        db.commit()
    return jsonify({"message": "Event updated successfully!"})

# Route to delete an event
@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM Events WHERE id = %s", (event_id,))
        db.commit()
    return jsonify({"message": "Event deleted successfully!"})

# Attachments Management API

@app.route('/attachments', methods=['GET'])
def attachments_page():
    """
    Render the attachments management page.
    """
    return render_template('attachments.html')

# Route to get all attachments
@app.route('/attachments', methods=['GET'])
def get_attachments():
    """
    Fetch all attachments from the Attachments table.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Attachments")
        attachments = cursor.fetchall()
    return jsonify(attachments)

# Route to add a new attachment
@app.route('/attachments', methods=['POST'])
def add_attachment():
    """
    Add a new attachment to the Attachments table.
    Requires: interaction_id or event_id, filename, file_url, and uploaded_by in the request body.
    """
    data = request.get_json()
    interaction_id = data.get('interaction_id')
    event_id = data.get('event_id')
    filename = data.get('filename')
    file_url = data.get('file_url')
    uploaded_by = data.get('uploaded_by')

    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Attachments (interaction_id, event_id, filename, file_url, uploaded_by) "
            "VALUES (%s, %s, %s, %s, %s)",
            (interaction_id, event_id, filename, file_url, uploaded_by)
        )
        db.commit()
    return jsonify({"message": "Attachment added successfully!"}), 201

# Route to get a specific attachment by ID
@app.route('/attachments/<int:attachment_id>', methods=['GET'])
def get_attachment(attachment_id):
    """
    Fetch an attachment by its unique ID.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Attachments WHERE id = %s", (attachment_id,))
        attachment = cursor.fetchone()
    if attachment:
        return jsonify(attachment)
    else:
        return jsonify({"error": "Attachment not found"}), 404

# Route to delete an attachment by ID
@app.route('/attachments/<int:attachment_id>', methods=['DELETE'])
def delete_attachment(attachment_id):
    """
    Delete an attachment by its unique ID.
    """
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM Attachments WHERE id = %s", (attachment_id,))
        db.commit()
    return jsonify({"message": "Attachment deleted successfully!"})

# AI Tools Log Management API

# Route to get all AI tools log entries
@app.route('/ai-tools-log', methods=['GET'])
def get_ai_tools_log():
    """
    Fetch all AI tools log entries from the AI_Tools_Log table.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM AI_Tools_Log")
        log_entries = cursor.fetchall()
    return jsonify(log_entries)

# Route to add a new AI tools log entry
@app.route('/ai-tools-log', methods=['POST'])
def add_ai_tools_log():
    """
    Add a new entry to the AI_Tools_Log table.
    Requires: user_id, query, and optionally response in the request body.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    query = data.get('query')
    response = data.get('response')

    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO AI_Tools_Log (user_id, query, response) VALUES (%s, %s, %s)",
            (user_id, query, response)
        )
        db.commit()
    return jsonify({"message": "AI tools log entry added successfully!"}), 201

# Route to get a specific AI tools log entry by ID
@app.route('/ai-tools-log/<int:log_id>', methods=['GET'])
def get_ai_tools_log_entry(log_id):
    """
    Fetch an AI tools log entry by its unique ID.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM AI_Tools_Log WHERE id = %s", (log_id,))
        log_entry = cursor.fetchone()
    if log_entry:
        return jsonify(log_entry)
    else:
        return jsonify({"error": "AI tools log entry not found"}), 404

# Statistics API

@app.route('/stats/user/<int:user_id>', methods=['GET'])
def user_statistics(user_id):
    """
    Get statistics for a specific user, including the number of events organized
    and interactions participated in.
    """
    with db.cursor() as cursor:
        # Get event count
        cursor.execute("SELECT COUNT(*) AS event_count FROM Events WHERE organizer_id = %s", (user_id,))
        event_count = cursor.fetchone()['event_count']

        # Get interaction count
        cursor.execute("SELECT COUNT(*) AS interaction_count FROM Interactions WHERE user_id = %s", 
(user_id,))
        interaction_count = cursor.fetchone()['interaction_count']

    return jsonify({
        "user_id": user_id,
        "event_count": event_count,
        "interaction_count": interaction_count
    })

@app.route('/user/<int:user_id>/interactions', methods=['GET'])
def user_interactions(user_id):
    """
    Fetch all interactions for a specific user.
    """
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Interactions WHERE user_id = %s", (user_id,))
        interactions = cursor.fetchall()
    return jsonify(interactions)

if __name__ == '__main__':
    app.run(debug=True)




