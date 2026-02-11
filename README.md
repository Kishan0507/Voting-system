# School Voting System

A Django-based web application for managing school elections.

## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Setup Instructions

1.  **Install Dependencies**

    Navigate to the project directory and install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Database Setup**

    Apply the database migrations to set up the database schema:

    ```bash
    python manage.py migrate
    ```

3.  **Create Sample Data (Optional but Recommended)**

    Run the provided script to populate the database with initial users (Principal, Teacher, Students) and election settings:

    ```bash
    python create_sample_data.py
    ```

    This will create:
    - **Principal**: Username: `principal`, Password: `admin123`
    - **Teacher**: Username: `teacher1`, Password: `teacher123`
    - **Students**:
        - John Doe (Aadhaar: `111122223333`, Password: `9876543210`)
        - Jane Smith (Aadhaar: `444455556666`, Password: `9123456780`)
        - Bob Wilson (Aadhaar: `777788889999`, Password: `9988776655`)
    - **Position**: School Captain
    - **Election Settings**: Active for 7 days

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

Open your web browser and go to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## User Roles & Login

- **Principal**: Can manage teachers, view results, and configure election settings.
- **Teacher**: Can manage students and nominate candidates.
- **Student**: Can view candidates and vote.

## Project Structure

- `manage.py`: Django's command-line utility.
- `school_voting/`: Project configuration.
- `core/`: Main application containing models, views, and forms.
- `templates/`: HTML templates.
- `requirements.txt`: Project dependencies.
