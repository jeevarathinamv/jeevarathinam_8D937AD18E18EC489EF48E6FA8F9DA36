"""
Raja Raja Cholan - The History of the Great Tamil Emperor
Flask Application Backend
"""

import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from database import query_db, execute_db, init_db, is_using_sqlite

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'raja_raja_cholan_imperial_secret_key_985_1014')

# Initialize DB on application startup
with app.app_context():
    init_db()

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Access restricted. Please log in with admin credentials.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Public Routes ---

@app.route('/')
def index():
    """Home Page with hero banner, quote, highlights, and quick access."""
    featured_articles = query_db(
        "SELECT * FROM articles WHERE is_featured = 1 ORDER BY id ASC LIMIT 4"
    )
    gallery_preview = query_db(
        "SELECT * FROM gallery ORDER BY id ASC LIMIT 4"
    )
    quote = {
        'tamil': 'அருண்மொழிவர்மனின் ஆட்சியில் அறமும் வீரமும் இணைந்த பேரரசின் பொற்காலம் மலர்ந்தது.',
        'translation': 'In the reign of Arulmozhivarman, a golden epoch blossomed where imperial valor and righteous governance walked hand in hand.',
        'author': 'Prof. K. A. Nilakanta Sastri',
        'work': 'The Cholas (1935)'
    }
    return render_template(
        'index.html',
        featured_articles=featured_articles,
        gallery_preview=gallery_preview,
        quote=quote,
        active_page='home'
    )

@app.route('/history')
def history():
    """Chronological biography and timeline of Raja Raja Cholan."""
    articles = query_db("SELECT * FROM articles WHERE category = %s ORDER BY id ASC", ('history',))
    return render_template('history.html', articles=articles, active_page='history')

@app.route('/military')
def military():
    """Military expeditions, naval supremacy, and imperial conquests."""
    articles = query_db("SELECT * FROM articles WHERE category = %s ORDER BY id ASC", ('military',))
    return render_template('military.html', articles=articles, active_page='military')

@app.route('/temple')
def temple():
    """Thanjavur Brihadeeswarar Temple architecture and historical grandeur."""
    articles = query_db("SELECT * FROM articles WHERE category = %s ORDER BY id ASC", ('temple',))
    temple_gallery = query_db("SELECT * FROM gallery WHERE category IN ('temple', 'architecture', 'sculptures')")
    return render_template('temple.html', articles=articles, gallery=temple_gallery, active_page='temple')

@app.route('/kingdom')
def kingdom():
    """Chola Empire administration, land surveys, economy, and culture."""
    articles = query_db("SELECT * FROM articles WHERE category = %s ORDER BY id ASC", ('kingdom',))
    return render_template('kingdom.html', articles=articles, active_page='kingdom')

@app.route('/achievements')
def achievements():
    """Key historical, cultural, and administrative achievements."""
    articles = query_db("SELECT * FROM articles WHERE category = %s ORDER BY id ASC", ('achievements',))
    all_articles = query_db("SELECT * FROM articles ORDER BY id ASC")
    return render_template('achievements.html', articles=articles, all_articles=all_articles, active_page='achievements')

@app.route('/gallery')
def gallery():
    """Visual gallery of Raja Raja Cholan era, architecture, and sculptures."""
    items = query_db("SELECT * FROM gallery ORDER BY id DESC")
    categories = sorted(list(set(item['category'] for item in items)))
    return render_template('gallery.html', items=items, categories=categories, active_page='gallery')

@app.route('/quiz')
def quiz():
    """Interactive quiz page on Raja Raja Cholan."""
    return render_template('quiz.html', active_page='quiz')

@app.route('/api/quiz', methods=['GET'])
def api_quiz():
    """API endpoint providing quiz questions in JSON format."""
    questions = query_db("SELECT id, question, option_a, option_b, option_c, option_d, correct_option, explanation FROM quiz_questions ORDER BY id ASC")
    return jsonify({'status': 'success', 'questions': questions, 'total': len(questions)})

# --- Admin Authentication & Dashboard Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('admin_login.html', active_page='admin')

        admin = query_db("SELECT * FROM admins WHERE username = %s", (username,), one=True)

        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session['admin_name'] = admin['full_name']
            flash(f"Welcome, {admin['full_name']}! You are logged in to the Emperor's Archives.", 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials. Please verify your username and password.', 'danger')

    return render_template('admin_login.html', active_page='admin')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.clear()
    flash('You have been securely logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin management dashboard."""
    articles = query_db("SELECT * FROM articles ORDER BY id DESC")
    gallery_items = query_db("SELECT * FROM gallery ORDER BY id DESC")
    quiz_questions = query_db("SELECT * FROM quiz_questions ORDER BY id DESC")

    stats = {
        'total_articles': len(articles),
        'total_gallery': len(gallery_items),
        'total_quiz': len(quiz_questions),
        'database_engine': 'SQLite (Local Sandbox)' if is_using_sqlite() else 'MySQL (XAMPP)'
    }

    return render_template(
        'admin_dashboard.html',
        articles=articles,
        gallery_items=gallery_items,
        quiz_questions=quiz_questions,
        stats=stats,
        active_page='admin'
    )

# --- Article Management ---

@app.route('/admin/article/add', methods=['POST'])
@admin_required
def admin_article_add():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    era_year = request.form.get('era_year', '').strip()
    summary = request.form.get('summary', '').strip()
    content = request.form.get('content', '').strip()
    image_url = request.form.get('image_url', '').strip() or '/static/images/thanjavur_temple.svg'
    is_featured = 1 if request.form.get('is_featured') else 0

    if not title or not category or not summary or not content:
        flash('Title, category, summary, and content are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    execute_db(
        "INSERT INTO articles (title, category, era_year, summary, content, image_url, is_featured) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (title, category, era_year, summary, content, image_url, is_featured)
    )
    flash(f'Article "{title}" published successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/article/edit/<int:article_id>', methods=['POST'])
@admin_required
def admin_article_edit(article_id):
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    era_year = request.form.get('era_year', '').strip()
    summary = request.form.get('summary', '').strip()
    content = request.form.get('content', '').strip()
    image_url = request.form.get('image_url', '').strip() or '/static/images/thanjavur_temple.svg'
    is_featured = 1 if request.form.get('is_featured') else 0

    if not title or not category or not summary or not content:
        flash('All required fields must be filled.', 'danger')
        return redirect(url_for('admin_dashboard'))

    execute_db(
        "UPDATE articles SET title = %s, category = %s, era_year = %s, summary = %s, content = %s, image_url = %s, is_featured = %s WHERE id = %s",
        (title, category, era_year, summary, content, image_url, is_featured, article_id)
    )
    flash(f'Article #{article_id} updated successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/article/delete/<int:article_id>', methods=['POST'])
@admin_required
def admin_article_delete(article_id):
    execute_db("DELETE FROM articles WHERE id = %s", (article_id,))
    flash(f'Article #{article_id} deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

# --- Gallery Management ---

@app.route('/admin/gallery/add', methods=['POST'])
@admin_required
def admin_gallery_add():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    image_url = request.form.get('image_url', '').strip() or '/static/images/thanjavur_temple.svg'
    attribution = request.form.get('attribution', '').strip() or 'Historical Archive / Public Domain'

    if not title or not category or not description:
        flash('Title, category, and description are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    execute_db(
        "INSERT INTO gallery (title, category, description, image_url, attribution) VALUES (%s, %s, %s, %s, %s)",
        (title, category, description, image_url, attribution)
    )
    flash(f'Gallery entry "{title}" added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/gallery/delete/<int:gallery_id>', methods=['POST'])
@admin_required
def admin_gallery_delete(gallery_id):
    execute_db("DELETE FROM gallery WHERE id = %s", (gallery_id,))
    flash(f'Gallery item #{gallery_id} deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

# --- Quiz Question Management ---

@app.route('/admin/quiz/add', methods=['POST'])
@admin_required
def admin_quiz_add():
    question = request.form.get('question', '').strip()
    option_a = request.form.get('option_a', '').strip()
    option_b = request.form.get('option_b', '').strip()
    option_c = request.form.get('option_c', '').strip()
    option_d = request.form.get('option_d', '').strip()
    correct_option = request.form.get('correct_option', '').strip().upper()
    explanation = request.form.get('explanation', '').strip()

    if not question or not option_a or not option_b or not option_c or not option_d or correct_option not in ('A', 'B', 'C', 'D'):
        flash('Question, 4 options, and a valid correct option (A, B, C, or D) are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    execute_db(
        "INSERT INTO quiz_questions (question, option_a, option_b, option_c, option_d, correct_option, explanation) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (question, option_a, option_b, option_c, option_d, correct_option, explanation)
    )
    flash('New quiz question added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/quiz/delete/<int:question_id>', methods=['POST'])
@admin_required
def admin_quiz_delete(question_id):
    execute_db("DELETE FROM quiz_questions WHERE id = %s", (question_id,))
    flash(f'Quiz question #{question_id} deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
