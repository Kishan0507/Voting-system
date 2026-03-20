# School Voting System 🗳️

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

A modern, highly secure, and visually stunning web application built with Django to manage internal school elections. Features independent dashboards for Principals, Teachers, and Students, alongside a cutting-edge Glassmorphism interface.

## 🌟 Key Features

**🔒 Secure User Roles:**
*   **Principal**: Master control over the election lifecycle. Add/remove teachers and students, revoke candidates, schedule the election timeframe, and publish results.
*   **Teachers**: Manage their assigned classrooms. Bulk-view student details and exclusively nominate outstanding students from their class for specific election positions.
*   **Students**: A fluid, lock-step voting experience. Can securely cast a single vote per position when the election is active.

**✨ Premium UI/UX:**
*   **Glassmorphism Engine**: Entire interface built with state-of-the-art floating glass cards, blur backdrops, and interactive hover states.
*   **Visual Voting Booth**: Modern radio button interactions that snap lively with checkmarks.
*   **Live Neo-Charting**: Election results rendered seamlessly via Chart.js using custom gradient-filled bar graphs.

**🛡️ Fortified Security:**
*   **Aadhaar Integration**: Unique Aadhaar mapping ensures absolutely no duplicate student accounts.
*   **Anti-Spoofing Architecture**: Backend natively guards against HTML payload manipulation to prevent positional candidate swapping.
*   **Single-Candidacy Restraint**: A student is computationally locked to running for only one single position per election phase.

## 🚀 Quickstart Guide

### 1. Installation
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/yourusername/school-voting-system.git
cd school-voting-system
pip install -r requirements.txt
```

### 2. Database Setup & Migrations
Initialize the fresh SQLite database:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Smart Seeding (Optional but Recommended)
Populate the empty database with a massive batch of ultra-realistic mock data instantly (1 Principal, 10 Teachers, 1000 Students, and standard Electoral Positions):
```bash
python seed.py
```
*The script will output the default login credentials in your terminal perfectly formatted!*

### 4. Run the Server
Boot up the development server:
```bash
python manage.py runserver
```
Visit `http://localhost:8000/` and sign in.

## 🧰 Built With
*   **Backend**: Django 4.2+, Python 3.13
*   **Frontend**: HTML5, custom vanilla CSS (Glassmorphism design system), Bootstrap 5 (Crispy Forms)
*   **Database**: SQLite (Default) // *Easily scalable to PostgreSQL*
*   **Data Visualization**: Chart.js (Live Election Tracking)
*   **Mocking**: Faker (for deterministic database seeding)

## 📁 Repository Structure
```text
📦 school-voting-system
 ┣ 📂 core/                # Main Django application (Models, Views, Forms, URLs)
 ┣ 📂 templates/           # Premium Glassmorphism UI components & Pages
 ┣ 📂 static/              # Local CSS overrides and JS assets
 ┣ 📜 seed.py              # Dedicated deterministic database seeder
 ┣ 📜 manage.py            # Django command-line utility
 ┣ 📜 requirements.txt     # Python dependency lockfile
 ┗ 📜 README.md            # Repository documentation
```

## ⚙️ Administrative Actions
- To manage users manually via Django Superuser: `python manage.py createsuperuser` and visit `/admin/`.
- All normal moderation (deleting candidates/users, dropping databases, toggling live results) should be performed via the **Principal Dashboard** root interface.

<br>
<p align="center"><i>Designed and Developed for seamless structural governance.</i></p>
