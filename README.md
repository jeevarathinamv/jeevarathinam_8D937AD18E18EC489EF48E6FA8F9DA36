# Raja Raja Cholan – The History of the Great Tamil Emperor

A colorful, beginner-friendly, and unique Historical Information Web Application built for MCA Mini Project, college demonstration, project viva, and YouTube coding presentations.

---

## 🌟 Project Overview

**Raja Raja Cholan – The History of the Great Tamil Emperor** is an interactive web portal celebrating the life, monumental conquests, naval power, brilliant administrative acumen, and architectural legacy of the great Chola monarch Arulmozhivarman (reigned 985–1014 CE).

The web application features:
- **Royal Historical Theme:** Designed with Royal Gold, Dark Maroon, Bronze, Royal Red, Cream, and Black with smooth animations and responsive Bootstrap 5 components.
- **Dedicated Historical Sections:**
  - **Home:** Hero presentation, famous Thanjavur Big Temple background, core achievements, and famous quote with attribution.
  - **History & Biography:** Life timeline from birth, family lineage, accession, milestones, to his final years.
  - **Military Expeditions:** Chola kingdom expansion, northern/southern campaigns, legendary Chola naval fleet, and key victories.
  - **Brihadeeswarar Temple (Thanjavur Big Temple):** Architectural marvels, 80-tonne granite Kumbam engineering, inscriptions, vimana, and sacred history.
  - **Chola Kingdom & Administration:** Valanadu revenue division, land survey, agrarian canal network, and maritime trade routes.
  - **Key Achievements:** Interactive cards detailing his monumental accomplishments.
  - **Historical Image Gallery:** Curated SVG historical artwork and sculptures with custom modal lightbox.
  - **Interactive Historical Quiz:** Dynamic MCQ engine powered by JavaScript and backed by MySQL/SQLite database.
- **Admin Dashboard:** Secure session-authenticated management system allowing administrators to:
  - Add, edit, and delete historical articles.
  - Add and remove gallery items.
  - Create and manage interactive quiz questions.
  - Monitor live dashboard statistics.
- **Dual Database Architecture:** Built to run directly on **MySQL via XAMPP** (using PyMySQL and parameterized SQL queries) with zero-configuration fallback to local SQLite for rapid testing.

---

## 🛠️ Technologies Used

- **Frontend:** HTML5, CSS3, Bootstrap 5.3, JavaScript (ES6+), Font Awesome 6
- **Backend:** Python 3 (Flask framework)
- **Database:** MySQL (XAMPP Server)
- **Python-MySQL Connector:** PyMySQL
- **Code Editor:** Visual Studio Code (VS Code)

---

## 📁 Project Structure

```text
├── app.py                     # Flask application routes, authentication, and API endpoints
├── database.py                # Database connection manager (PyMySQL with SQLite fallback)
├── database.sql               # MySQL database schema and historical seed data
├── requirements.txt           # Python dependencies
├── test_app.py                # Automated test suite (6/6 unit tests)
├── README.md                  # Comprehensive setup guide and project documentation
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Base layout with navbar, footer, and styling
│   ├── index.html             # Home page with hero, quote, and quick links
│   ├── history.html           # Timeline of Raja Raja Cholan's life and reign
│   ├── military.html          # Military conquests, campaigns, and naval supremacy
│   ├── temple.html            # Brihadeeswarar Temple architecture and history
│   ├── kingdom.html           # Administration, land revenue, trade, and culture
│   ├── achievements.html      # Comprehensive achievements breakdown
│   ├── gallery.html           # Interactive image gallery with modal view
│   ├── quiz.html              # Interactive multiple-choice historical quiz
│   ├── admin_login.html       # Secure administrative login portal
│   └── admin_dashboard.html   # Admin dashboard for articles, gallery, and quiz CRUD
└── static/
    ├── css/
    │   └── style.css          # Royal custom theme styling, cards, and animations
    ├── js/
    │   └── script.js          # Interactive quiz engine and image modal preview
    └── images/                # Original SVG vector illustrations & portraits
        ├── thanjavur_temple.svg
        ├── rajaraja_portrait.svg
        ├── chola_navy.svg
        ├── nataraja_bronze.svg
        ├── chola_emblem.svg
        └── administration.svg
```

---

## 🔑 Default Admin Credentials

For college demonstration, project viva, and testing:

| Username | Password | Role |
| :--- | :--- | :--- |
| `admin` | `admin123` | Super Administrator |

*(Passwords are securely hashed using Werkzeug `scrypt`/`pbkdf2:sha256` encryption).*

---

## 💻 Step-by-Step Windows & VS Code Setup Instructions

Follow these exact steps to run the project on a Windows machine with VS Code and XAMPP:

### Step 1: Install Prerequisites
1. **Python 3:** Download and install Python (3.9 or higher) from [python.org](https://www.python.org/). *Ensure you check the box **"Add Python to PATH"** during installation.*
2. **XAMPP:** Download and install XAMPP with Apache and MySQL from [apachefriends.org](https://www.apachefriends.org/).
3. **VS Code:** Download and install Visual Studio Code from [code.visualstudio.com](https://code.visualstudio.com/).

### Step 2: Start Apache and MySQL in XAMPP
1. Launch the **XAMPP Control Panel** as Administrator.
2. Click **Start** next to **Apache**.
3. Click **Start** next to **MySQL**.
4. Ensure both services show green status indicators.

### Step 3: Create and Import Database in phpMyAdmin
1. Open your web browser and navigate to:
   ```text
   http://localhost/phpmyadmin/
   ```
2. Click on the **Databases** tab at the top.
3. Under *Create database*, enter the database name:
   ```text
   raja_raja_cholan_db
   ```
4. Choose collation `utf8mb4_unicode_ci` and click **Create**.
5. Select `raja_raja_cholan_db` from the left sidebar.
6. Click on the **Import** tab in the top menu.
7. Click **Choose File** (or *Browse*) and select `database.sql` located inside your project folder.
8. Scroll to the bottom and click **Import** (or **Go**).
9. All 4 tables (`admins`, `articles`, `gallery`, `quiz_questions`) and sample historical records will be created.

### Step 4: Open Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File** -> **Open Folder...** and select the project directory.
3. Open a new terminal in VS Code: `Ctrl + \`` or `Terminal` -> `New Terminal`.

### Step 5: Install Required Python Packages
In the VS Code terminal, execute:
```bash
pip install -r requirements.txt
```

### Step 6: Verify Database Configuration
Open `database.py` in VS Code and confirm your local MySQL credentials:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # Default XAMPP MySQL password is empty
    'database': 'raja_raja_cholan_db',
    'charset': 'utf8mb4'
}
```
*(If your XAMPP MySQL uses a different port or password, update the dictionary accordingly).*

### Step 7: Run the Flask Application
In the VS Code terminal, start the server:
```bash
python app.py
```

You should see output similar to:
```text
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

### Step 8: View the Website in Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```
You can now explore the website, read historical accounts, play the quiz, and log in to the Admin Dashboard at `http://127.0.0.1:5000/admin/login`!

---

## 🧪 Running Automated Tests

To run the automated test suite verifying all routes, database transactions, quiz scoring API, and administrative functions:
```bash
python -m unittest test_app.py
```

---

## 📚 Historical References & Image Attribution

### Historical References
- **Nilakanta Sastri, K. A.** (1935). *The Colas*. University of Madras.
- **Balasubrahmanyam, S. R.** (1975). *Middle Chola Temples: Rajaraja I to Rajendra I (A.D. 985–1070)*. Thomson Press.
- **Epigraphia Carnatica & South Indian Inscriptions (SII)**, Archaeological Survey of India (ASI) volumes recording Thanjavur temple inscriptions and copper plates.
- **Kalki Krishnamurthy** (1954). *Ponniyin Selvan* (Historical context and popular Tamil cultural history).

### Vector Artwork & Media Attribution
- All illustrations located in `static/images/` are custom original SVG historical vector artworks created for this project:
  - `thanjavur_temple.svg`: Geometric vector rendering of the Brihadeeswarar Temple Vimana and sanctum.
  - `rajaraja_portrait.svg`: Stylized historical artistic illustration of Emperor Raja Raja Cholan I.
  - `chola_navy.svg`: Artistic depiction of medieval Chola maritime naval vessels.
  - `nataraja_bronze.svg`: Vector tribute to classic Chola lost-wax bronze casting art.
  - `chola_emblem.svg`: Traditional Chola royal tiger crest emblem.
  - `administration.svg`: Artistic illustration of temple inscriptions, palm-leaf records, and agrarian revenue management.

---

## 🛡️ Security Features
- **Parameterized SQL Queries:** Prevents SQL Injection by passing all user input as tuples to prepared SQL queries.
- **Cryptographic Password Hashing:** Secure admin authentication with salted password hashes.
- **Session Authentication:** Role-protected admin routes requiring valid active sessions.
- **Input Validation:** Backend verification of required fields before executing database insert or update operations.

---

## 📜 License
Developed as an educational showcase and open-source college project. All original illustrations, source code, and historical narratives are released for educational and academic submission purposes.
