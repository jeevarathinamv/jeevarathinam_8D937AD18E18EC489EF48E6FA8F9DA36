"""
Database Connection & Management Module for Raja Raja Cholan Website.
Connects with MySQL (XAMPP / PyMySQL) with fallback to SQLite for local standalone execution.
"""

import os
import pymysql
from pymysql.cursors import DictCursor
import sqlite3
from werkzeug.security import generate_password_hash

# Database Configuration (Defaults for XAMPP MySQL)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'raja_raja_cholan_db')
DB_PORT = int(os.environ.get('DB_PORT', 3306))

# Fallback SQLite DB path
SQLITE_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'raja_raja_cholan.db')
USE_SQLITE_ENV = os.environ.get('USE_SQLITE', '').lower() in ('1', 'true', 'yes')

def is_using_sqlite():
    """Checks whether the application should use SQLite or MySQL."""
    if USE_SQLITE_ENV:
        return True
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=2
        )
        conn.close()
        return False
    except Exception:
        # Fallback to SQLite if MySQL is not reachable
        return True

def get_connection():
    """Returns an active database connection and connection type ('sqlite' or 'mysql')."""
    if is_using_sqlite():
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'
    else:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=DictCursor,
            autocommit=True
        )
        return conn, 'mysql'

def query_db(query, args=(), one=False):
    """Executes a SELECT query with parameters and returns dictionary rows."""
    conn, engine = get_connection()
    try:
        if engine == 'sqlite':
            # Translate MySQL '%s' placeholders to SQLite '?' placeholders
            sqlite_query = query.replace('%s', '?')
            cur = conn.cursor()
            cur.execute(sqlite_query, args)
            rows = cur.fetchall()
            cur.close()
            result = [dict(row) for row in rows]
            return (result[0] if result else None) if one else result
        else:
            with conn.cursor() as cur:
                cur.execute(query, args)
                result = cur.fetchall()
                return (result[0] if result else None) if one else result
    finally:
        conn.close()

def execute_db(query, args=()):
    """Executes an INSERT, UPDATE, or DELETE query with parameters and returns the last row ID."""
    conn, engine = get_connection()
    try:
        if engine == 'sqlite':
            sqlite_query = query.replace('%s', '?')
            cur = conn.cursor()
            cur.execute(sqlite_query, args)
            conn.commit()
            last_id = cur.lastrowid
            cur.close()
            return last_id
        else:
            with conn.cursor() as cur:
                cur.execute(query, args)
                last_id = cur.lastrowid
                conn.commit()
                return last_id
    finally:
        conn.close()

def init_db():
    """Initializes the database schema and default seeds."""
    conn, engine = get_connection()
    try:
        if engine == 'sqlite':
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    era_year TEXT,
                    summary TEXT NOT NULL,
                    content TEXT NOT NULL,
                    image_url TEXT,
                    is_featured INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS gallery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    attribution TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS quiz_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,
                    option_d TEXT NOT NULL,
                    correct_option TEXT NOT NULL,
                    explanation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

            # Seed admin if empty
            cur.execute("SELECT COUNT(*) as count FROM admins")
            if cur.fetchone()[0] == 0:
                pwd_hash = generate_password_hash('admin123')
                cur.execute(
                    "INSERT INTO admins (username, password_hash, full_name, email) VALUES (?, ?, ?, ?)",
                    ('admin', pwd_hash, 'Chola Historian Administrator', 'admin@cholaheritage.org')
                )
                conn.commit()

            # Seed articles if empty
            cur.execute("SELECT COUNT(*) as count FROM articles")
            if cur.fetchone()[0] == 0:
                seed_articles = [
                    (
                        'The Ascent of Arulmozhivarman', 'history', '947 – 985 CE',
                        'Born as Arulmozhivarman, the prince stepped aside in favor of Uttama Chola before peacefully ascending the imperial throne as Raja Raja Cholan I.',
                        'Arulmozhivarman was born in Tirukoilur as the third child of Parantaka Sundara Chola and Queen Vanavan Mahadevi of the Malayaman dynasty. Following the mysterious demise of his heroic elder brother Aditya Karikalan, Tamil country was poised on the verge of civil unrest. Exhibiting profound magnanimity and statecraft, Arulmozhivarman declined immediate accession to honor his uncle Uttama Chola throne claim. In 985 CE, upon Uttama Cholas passing, he ascended the throne under the regnal title Rajakesari Arulmozhi Varman, heralding the golden era of the Chola Empire.',
                        '/static/images/rajaraja_portrait.svg', 1
                    ),
                    (
                        'Architectural Grandeur of Brihadeeswarar Temple', 'temple', '1003 – 1010 CE',
                        'Commissioned by Raja Raja Cholan, the Peruvudaiyar Kovil remains an engineering marvel with its 216-foot granite Vimana and 80-ton single stone Kumbam.',
                        'The Brihadeeswarar Temple (Peruvudaiyar Kovil) at Thanjavur is the pinnacle of Dravidian architectural mastery. Consecrated on the 275th day of his 25th regnal year in 1010 CE, the entire temple was erected using over 130,000 tons of granite in a delta plain devoid of natural stone. The colossal Vimana towers 216 feet into the sky, capped by an 80-ton monolithic granite cupola rolled into position across a 6-kilometer earthen ramp. Inscribed upon its walls are the names of every architect, stonemason, dancer, and singer who contributed, immortalizing their labor forever.',
                        '/static/images/thanjavur_temple.svg', 1
                    ),
                    (
                        'Maritime Navy and Kandalur Salai Triumph', 'military', '988 – 1008 CE',
                        'The Chola navy was one of the most formidable maritime fleets in Asian history, neutralizing Chera naval fleets and expanding imperial boundaries.',
                        'Raja Raja Cholan realized that control of Indian Ocean trade sea-lanes required an invincible maritime armada. His historic campaign against Kandalur Salai dismantled the Chera naval stronghold, establishing undisputed supremacy along the Malabar and Coromandel coasts. Subsequent maritime expeditions incorporated Anuradhapura and the northern territories of Sri Lanka (renamed Mummudi Chola Mandalam) as well as the Maldives (Munnir Pazhantivu Pannirayiram). These naval conquests safeguarded Tamil merchant guilds venturing to Srivijaya and the Song Empire of China.',
                        '/static/images/chola_navy.svg', 1
                    ),
                    (
                        'Revolutionary Revenue Survey and Administrative Division', 'kingdom', '986 – 1014 CE',
                        'Raja Raja Cholan implemented the historic land survey project in 1000 CE, classifying land quality and instituting democratic Ur and Sabha self-governance.',
                        'A master administrator, Raja Raja Cholan standardized revenue assessment through a comprehensive land survey across the entire empire, directed by his revenue minister Senapathi Kuravan Ulagalanthan. The kingdom was methodically divided into Valanadus, Nadus, and Urs. Inscriptions reveal the operation of autonomous village assemblies with strict eligibility criteria for village officials, fostering civic accountability, advanced canal irrigation maintenance, and famine relief granaries.',
                        '/static/images/administration.svg', 1
                    ),
                    (
                        'Recovery of the Sacred Thevaram Hymns', 'achievements', 'c. 1000 CE',
                        'Recognizing the danger of losing Saivite devotional literature, Raja Raja assisted Nambiyandar Nambi to unearth the sacred Thevaram palm leaves from Chidambaram.',
                        'One of Raja Raja Cholan most revered cultural contributions was the salvage and compilation of the Thevaram devotional hymns composed by Appar, Sambandar, and Sundarar. Locked away in an inner chamber behind sealed doors at the Chidambaram Nataraja Temple, the precious palm leaf manuscripts were decomposing. Raja Raja facilitated their respectful retrieval and engaged court musicians (Odhuvars) to set them to classical Pann modes, earning him the honorific title Tirumurai Kanda Cholan.',
                        '/static/images/nataraja_bronze.svg', 1
                    )
                ]
                cur.executemany(
                    "INSERT INTO articles (title, category, era_year, summary, content, image_url, is_featured) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    seed_articles
                )
                conn.commit()

            # Seed gallery if empty
            cur.execute("SELECT COUNT(*) as count FROM gallery")
            if cur.fetchone()[0] == 0:
                seed_gallery = [
                    ('Imperial Portrait of Emperor Raja Raja Cholan', 'portrait', 'Artistic historical visualization of Emperor Raja Raja Cholan adorned in royal regalia, pearl garlands, and the imperial Chola crown.', '/static/images/rajaraja_portrait.svg', 'Original Chola Heritage Vector Art (CC-BY-4.0)'),
                    ('Brihadeeswarar Temple - Tower of Majesty', 'temple', 'The imposing 216-foot Dravidian Vimana of Thanjavur Big Temple illuminated under the golden twilight sky.', '/static/images/thanjavur_temple.svg', 'Architectural Heritage Survey (Public Domain / Original)'),
                    ('Chola Royal Navy Fleet in the Bay of Bengal', 'warfare', 'Ancient Tamil war vessels navigating high seas with multi-oared galleys and heraldic tiger flags unfurled.', '/static/images/chola_navy.svg', 'Maritime History Archive (Original Illustration)'),
                    ('Sacred Bronze Nataraja of Chola Foundry', 'sculptures', 'World-celebrated lost-wax bronze sculpture of Lord Shiva in Ananda Tandava stance, epitomizing Chola artistic zenith.', '/static/images/nataraja_bronze.svg', 'Chola Bronze Metallurgy Collection (CC0)'),
                    ('Imperial Tiger Seal and Ancient Coinage', 'architecture', 'The iconic Royal Chola royal crest featuring the seated tiger flanked by Pandya double fish and Chera bow emblem.', '/static/images/chola_emblem.svg', 'Numismatic Society of South India Archive')
                ]
                cur.executemany(
                    "INSERT INTO gallery (title, category, description, image_url, attribution) VALUES (?, ?, ?, ?, ?)",
                    seed_gallery
                )
                conn.commit()

            # Seed quiz if empty
            cur.execute("SELECT COUNT(*) as count FROM quiz_questions")
            if cur.fetchone()[0] == 0:
                seed_quiz = [
                    ('What was the original birth name of Emperor Raja Raja Cholan I before his coronation?', 'Aditya Karikalan', 'Arulmozhivarman', 'Kulothunga', 'Rajendra', 'B', 'Raja Raja Cholan was originally named Arulmozhivarman, meaning "he whose speech is graced with benevolence".'),
                    ('In which year was the Brihadeeswarar Temple in Thanjavur consecrated by Raja Raja Cholan?', '985 CE', '1000 CE', '1010 CE', '1025 CE', 'C', 'The temple was consecrated on the 275th day of his 25th regnal year, which corresponds to 1010 CE.'),
                    ('Which title was bestowed upon Raja Raja Cholan for recovering and organizing the sacred Thevaram hymns?', 'Mummudi Cholan', 'Tirumurai Kanda Cholan', 'Jayamgonda Cholan', 'Sivapadasekhara', 'B', 'He was celebrated as "Tirumurai Kanda Cholan" (The one who discovered and organized the sacred Shaivite scriptures).'),
                    ('What is the approximate weight of the monolithic granite cupola sitting atop the Vimana of the Thanjavur Big Temple?', '20 Tons', '45 Tons', '80 Tons', '150 Tons', 'C', 'The monolithic granite capstone (Kumbam) weighs an astonishing 80 tons, hauled via a gentle ramp system.'),
                    ('Which naval battle is prominently recorded in Raja Raja Cholan inscriptions celebrating his early maritime conquest?', 'Battle of Takkolam', 'Kandalur Salai', 'Battle of Venni', 'Koppam Campaign', 'B', 'The conquest of Kandalur Salai (Kandalur Salai Kalamarutha) is eulogized in his royal inscriptions as his first major naval victory.'),
                    ('Which island kingdom was conquered and designated as "Mummudi Chola Mandalam" under Raja Raja Cholan rule?', 'Maldives', 'Java', 'Sri Lanka (Ceylon)', 'Sumatra', 'C', 'Northern Sri Lanka was incorporated into the Chola Empire as the province of Mummudi Chola Mandalam, with Polonnaruwa as capital.'),
                    ('What was the name of the revenue minister who led the historic imperial land survey of 1000 CE under Raja Raja Cholan?', 'Aniruddha Brahmadhiraja', 'Senapathi Kuravan Ulagalanthan', 'Bana Vidyadhara', 'Nambiyandar Nambi', 'B', 'Senapathi Kuravan Ulagalanthan directed the metric survey and valuation of agricultural lands across the empire.'),
                    ('What royal emblem appeared on the official seal and standard of the Imperial Cholas?', 'Bow and Arrow', 'Double Fish', 'Ferocious Tiger', 'Elephant', 'C', 'The leaping Tiger was the majestic dynastic emblem of the Cholas, often shown flanked by the fish of Pandyas and bow of Cheras.')
                ]
                cur.executemany(
                    "INSERT INTO quiz_questions (question, option_a, option_b, option_c, option_d, correct_option, explanation) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    seed_quiz
                )
                conn.commit()

            cur.close()
        else:
            # If MySQL is reachable, execute SQL if needed
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM admins")
    finally:
        conn.close()

if __name__ == '__main__':
    print("Initializing Database...")
    init_db()
    print("Database Initialized successfully.")
    articles = query_db("SELECT id, title, category FROM articles")
    print(f"Total articles seeded: {len(articles)}")
    for a in articles:
        print(f" - [{a['category']}] {a['title']}")
