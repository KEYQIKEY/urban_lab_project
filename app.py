import os
import logging
import csv
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, session, redirect, url_for, render_template, make_response
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
    
    
@app.route('/api/upload', methods=['POST'])
def upload_csv():
    """
    Handle CSV file upload and insert data into the database.
    """
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        # Decode CSV and insert into the database
        stream = file.stream.read().decode('utf-8')
        csv_reader = csv.DictReader(stream.splitlines())
        for row in csv_reader:
            # Customize for your specific table
            db.cursor().execute("""
                INSERT INTO YourTable (column1, column2, column3)
                VALUES (%s, %s, %s)
            """, (row['column1'], row['column2'], row['column3']))
        db.commit()
        return jsonify({"message": "Data uploaded successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error uploading CSV: {e}")
        return jsonify({"error": "Failed to upload data"}), 500
        
@app.route('/api/export', methods=['GET'])
def export_table():
    """
    Export data from a selected table.
    """
    table = request.args.get("table")
    valid_tables = ["events", "interactions", "users"]

    if table not in valid_tables:
        return jsonify({"error": "Invalid table name"}), 400

    try:
        # Query based on the selected table
        query_map = {
            "events": "SELECT id, name, description, event_date, location FROM events",
            "interactions": "SELECT id, user_id, interaction_type, details, interaction_date FROM interactions",
            "users": "SELECT id, name, email, user_type, organization FROM users"
        }
        query = query_map[table]

        with db.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        # Generate CSV
        csv_output = "id,name,description,event_date,location\n" if table == "events" else \
                     "id,user_id,interaction_type,details,interaction_date\n" if table == "interactions" else \
                     "id,name,email,user_type,organization\n"

        for row in results:
            csv_output += ",".join(str(value) for value in row) + "\n"

        # Return CSV as response
        response = make_response(csv_output)
        response.headers["Content-Disposition"] = f"attachment; filename={table}.csv"
        response.headers["Content-Type"] = "text/csv"
        return response

    except Exception as e:
        app.logger.error(f"Error exporting table {table}: {e}")
        return jsonify({"error": "Failed to export data"}), 500


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
    
@app.route('/api/interactions', methods=['GET'])
def get_interactions():
    """
    Fetch all interactions from the Interactions table.
    """
    try:
        with db.cursor() as cursor:
            
            cursor.execute("""
                SELECT 
                    id, 
                    user_id, 
                    interaction_type, 
                    details, 
                    DATE_FORMAT(interaction_date, '%Y-%m-%d') AS interaction_date
                FROM Interactions
            """)
            interactions = cursor.fetchall()

        
        return jsonify(interactions), 200
    except Exception as e:
        app.logger.error(f"Error fetching interactions: {e}")
        return jsonify({"error": "Failed to fetch interactions."}), 500




@app.route('/api/interactions/<int:interaction_id>', methods=['GET'])
def get_interaction_by_id(interaction_id):
    """
    Fetch a specific interaction by its ID.
    """
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM Interactions WHERE id = %s", (interaction_id,))
            interaction = cursor.fetchone()
        if interaction:
            return jsonify(interaction), 200
        else:
            return jsonify({"error": "Interaction not found"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching interaction: {e}")
        return jsonify({"error": "Failed to fetch interaction."}), 500


# Route to add a new interaction
@app.route('/api/interactions', methods=['POST'])
def add_interaction():
    """
    Add a new interaction to the Interactions table.
    """
    try:
        data = request.get_json()  
        user_id = data.get('user_id')
        interaction_type = data.get('interaction_type')
        details = data.get('details')
        interaction_date = data.get('interaction_date')

        if not all([user_id, interaction_type, details, interaction_date]):
            return jsonify({"error": "Missing required fields"}), 400

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
    except Exception as e:
        app.logger.error(f"Error adding interaction: {e}")
        return jsonify({"error": "Failed to add interaction."}), 500


# Route to update an interaction
@app.route('/api/interactions/<int:interaction_id>', methods=['PUT'])
def update_interaction(interaction_id):
    """
    Update an existing interaction by ID.
    """
    try:
        data = request.get_json()
        interaction_type = data.get('interaction_type')
        details = data.get('details')
        interaction_date = data.get('interaction_date')

        if not all([interaction_type, details, interaction_date]):
            return jsonify({"error": "Missing required fields"}), 400

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

        return jsonify({"message": "Interaction updated successfully!"}), 200
    except Exception as e:
        app.logger.error(f"Error updating interaction: {e}")
        return jsonify({"error": "Failed to update interaction."}), 500



# Route to delete an interaction
@app.route('/api/interactions/<int:interaction_id>', methods=['DELETE'])
def delete_interaction(interaction_id):
    """
    Delete an interaction by ID.
    """
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Interactions WHERE id = %s", (interaction_id,))
            db.commit()
        return jsonify({"message": "Interaction deleted successfully!"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting interaction: {e}")
        return jsonify({"error": "Failed to delete interaction."}), 500



# Events Management API

@app.route('/events', methods=['GET'])
def events_page():
    """
    Render the events management page.
    """
    return render_template('events.html')


@app.route('/api/events', methods=['GET'])
def api_get_events():
    """
    Fetch and return all events as JSON data.
    """
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                e.id, 
                e.name, 
                e.description, 
                DATE_FORMAT(e.event_date, '%Y-%m-%d') AS event_date, 
                e.location, 
                u.name AS organizer
            FROM Events e
            JOIN Users u ON e.organizer_id = u.id
        """)
        events = cursor.fetchall()
    return jsonify(events)




@app.route('/api/events', methods=['POST'])
def add_event():
    """
    Add a new event to the Events table.
    """
    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    event_date = data.get('event_date')
    location = data.get('location')
    organizer_id = data.get('organizer_id')

    if not all([name, description, event_date, location, organizer_id]):
        return jsonify({"error": "Missing required fields"}), 400

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


@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """
    Fetch an event by its unique ID.
    """
    try:
        with db.cursor() as cursor:
            
            cursor.execute("""
                SELECT 
                    e.id, 
                    e.name, 
                    e.description, 
                    DATE_FORMAT(e.event_date, '%Y-%m-%d') AS event_date, 
                    e.location, 
                    u.id AS organizer_id
                FROM Events e
                JOIN Users u ON e.organizer_id = u.id
                WHERE e.id = %s
            """, (event_id,))
            event = cursor.fetchone()

        
        if event:
            
            event_data = {
                "id": event["id"],
                "name": event["name"],
                "description": event["description"],
                "event_date": event["event_date"],
                "location": event["location"],
                "organizer_id": event["organizer_id"]
            }
            return jsonify(event_data)
        else:
            
            return jsonify({"error": "Event not found"}), 404

    except Exception as e:
        
        app.logger.error(f"Error fetching event with ID {event_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500





@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """
    Update an existing event by its ID.
    """
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    event_date = data.get('event_date')
    location = data.get('location')
    organizer_id = data.get('organizer_id')  

    if not all([name, description, event_date, location, organizer_id]):  
        return jsonify({"error": "Missing required fields"}), 400

    with db.cursor() as cursor:
        cursor.execute(
            """
            UPDATE Events
            SET name = %s, description = %s, event_date = %s, location = %s, organizer_id = %s
            WHERE id = %s
            """,
            (name, description, event_date, location, organizer_id, event_id)
        )
        db.commit()

    return jsonify({"message": "Event updated successfully!"})



@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """
    Delete an event by its ID.
    """
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM Events WHERE id = %s", (event_id,))
        db.commit()
    return jsonify({"message": "Event deleted successfully!"})

# AI Tools Log Management API


@app.route('/api/ai_tools', methods=['POST'])
def ai_tools():
    """
    Process a user's query, generate a response, and return it.
    """
    try:
        # 获取前端传来的查询数据
        data = request.get_json()
        user_id = data.get('user_id')  # 示例中提供的用户ID
        query = data.get('query')

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        # 假设AI的简单逻辑生成响应
        ai_response = f"AI Response for: {query}"  # 这里是模拟AI逻辑

        return jsonify({
            "query": query,
            "response": ai_response
        }), 200
    except Exception as e:
        app.logger.error(f"Error in AI Tools: {e}")
        return jsonify({"error": "Failed to process AI tools request."}), 500
        
        

        # 将日志数据返回给前端
        return jsonify(logs), 200
    except Exception as e:
        app.logger.error(f"Error fetching AI Tools logs: {e}")
        return jsonify({"error": "Failed to retrieve AI tools logs"}), 500




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

@app.route('/api/stats')
def get_stats():
    """
    Route to fetch and return interaction statistics and user growth data.
    """
    # SQL query for interaction type statistics
    interaction_query = """
        SELECT interaction_type, COUNT(id) AS count
        FROM interactions
        GROUP BY interaction_type
    """
    # SQL query for user growth statistics by month
    user_growth_query = """
        SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(id) AS 
count
        FROM users
        GROUP BY month
        ORDER BY month
    """
    
    # SQL query for total events count
    total_events_query = """
        SELECT COUNT(*) AS total_events
        FROM events
    """
    

    try:
        # Initialize empty data structures
        interaction_data = {}
        user_growth_data = []
        total_events = 0

        # Execute SQL queries
        with db.cursor() as cursor:
            # Fetch interaction statistics
            cursor.execute(interaction_query)
            interaction_stats = cursor.fetchall()
            for row in interaction_stats:
                interaction_data[row['interaction_type']] = row['count']

            # Fetch user growth statistics
            cursor.execute(user_growth_query)
            user_growth_stats = cursor.fetchall()
            for row in user_growth_stats:
                user_growth_data.append({
                    "month": row['month'],
                    "count": row['count']
                })
                
            # Fetch total events count
            cursor.execute(total_events_query)
            total_events_result = cursor.fetchone()
            total_events = total_events_result['total_events']


        # Format the response as JSON
        return jsonify({
            "interaction_data": interaction_data,
            "user_growth_data": user_growth_data,
            "total_events": total_events
        })

    except Exception as e:
        # Log the error and return an appropriate response
        app.logger.error(f"Database query failed: {e}")
        return jsonify({"error": "Failed to retrieve statistics"}), 500

if __name__ == '__main__':
    app.run(debug=True)




