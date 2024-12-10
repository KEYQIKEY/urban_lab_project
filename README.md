# Urban Lab Contact Database Development

## Project Overview
This project involves the development of a centralized contact support database for 
**Urban Lab**, aimed at urban development and sustainability. The system is designed 
to efficiently manage stakeholder interactions, track events, and facilitate 
reporting.

## Features
- **User Management**: CRUD operations (Create, Read, Update, Delete) for managing 
user data.
- **Event Tracking**: Records details of events including name, date, location, and 
organizer.
- **Interaction Logging**: Tracks interactions with stakeholders (e.g., meetings, 
emails).
- **AI Integration**: Future AI-powered query and analytics support.

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, Bootstrap
- **Version Control**: Git, GitHub

## Installation Guide

1. Clone the Repository
To get started, clone the repository to your local machine:
```bash
git clone https://github.com/yourusername/urban-lab-contact-database.git

2. Install Dependencies
Install the required Python packages using the following command:
pip install -r requirements.txt

3. Database Setup
Create a MySQL database and import the schema found in the db_schema.sql file:
-- Example SQL for setting up the database
CREATE DATABASE urban_lab;
USE urban_lab;
-- Paste the contents of db_schema.sql here

4. Run the Application
Start the Flask application:

python app.py

The application will run locally at http://127.0.0.1:5000/.

Usage
Login: Admin users can log in using credentials defined in the users table.
Dashboard: View real-time statistics such as the total number of users, events, and 
	interactions.
User Management: Manage users and roles (e.g., student, client).
Event Management: Track events and manage associated details.
Interaction Management: Log and manage interactions with stakeholders.

Future Enhancements
Fully integrate AI for advanced query functionality.
Enhanced analytics dashboards for visual insights into stakeholder interactions.
Scale the system to support more types of stakeholders and interactions.

Contact
For questions or contributions, contact me at [your-email@example.com].

---

### **Detailed English Guide (for Installation and Setup)**

#### **Step 2: Install Dependencies**

1. **Ensure Python and pip are installed**:
   - Please ensure that **Python** and **pip** (Python package manager) are 
installed on your system. If not, you can download and install Python from [Python's 
official website](https://www.python.org/downloads/).
   
   - If needed, update **pip** by running:
     ```bash
     python -m ensurepip --upgrade
     ```

2. **Create a Virtual Environment** (Recommended):
   - To avoid dependency conflicts, it’s recommended to set up a virtual 
environment. Create a virtual environment by running:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - For **Windows** users:
       ```bash
       .\venv\Scripts\activate
       ```
     - For **Mac/Linux** users:
       ```bash
       source venv/bin/activate
       ```

3. **Install Project Dependencies**:
   - In the project’s root directory, find the `requirements.txt` file, which lists 
all necessary dependencies. Install them using the following command:
     ```bash
     pip install -r requirements.txt
     ```

4. **Verify the Installation**:
   - After installation, verify that the dependencies have been successfully 
installed by running:
     ```bash
     pip list
     ```
   - This will list all installed packages and their versions.

5. **If you encounter any issues**:
   - Ensure that your **Python** and **pip** are up-to-date. If you encounter errors 
during installation, try updating pip:
     ```bash
     python -m pip install --upgrade pip
     ```

---

#### **Step 3: Database Setup**

1. **Create the Database**:
   - Open your MySQL client (like MySQL Workbench or the command line) and create a 
new database:
     ```sql
     CREATE DATABASE urban_lab;
     ```

2. **Import the Database Schema**:
   - In the project folder, find the `db_schema.sql` file. Use the following command 
to import the schema into your MySQL database:
     ```bash
     mysql -u root -p < db_schema.sql
     ```
   - This will create the required tables and relationships in the database.

3. **Check the Database**:
   - Ensure that the tables have been successfully created. You can check this by 
running:
     ```sql
     SHOW TABLES;
     ```

---

#### **Step 4: Run the Application**

1. **Start the Flask Application**:
   - Ensure that your virtual environment is activated and all dependencies are 
installed. Then, run the following command to start the Flask application:
     ```bash
     python app.py
     ```

2. **Access the Application Locally**:
   - Once the application is running, open your browser and visit 
`http://127.0.0.1:5000/` to access the system.

3. **Common Issues**:
   - If you encounter the "Port 5000 already in use" error, try changing the port:
     ```bash
     python app.py runserver 5001
     ```

---

### **Summary**

By following these steps, you should be able to set up and run the project 
successfully. If you have any questions or run into issues during the setup, feel 
free to contact me or refer to the GitHub repository for more details. If you'd like 
to contribute or suggest any improvements, please open an issue or submit a pull 
request!

---
