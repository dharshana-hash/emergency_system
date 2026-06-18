import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'emergency_system_ultra_secure_secret_token_key'

# --- SAFE WINDOWS SQLITE STORAGE PATH ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE SCHEMAS ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Admin' or 'Volunteer'

class HelpRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    disaster_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.Integer, nullable=False)
    priority_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, In Progress, Completed
    assigned_volunteer = db.Column(db.String(100), default='Unassigned')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def calculate_priority(disaster_type, severity):
    weights = {"Earthquake": 10, "Flood": 9, "Cyclone": 8, "Landslide": 7}
    d_weight = weights.get(disaster_type, 5)
    return round((d_weight * 0.6) + (int(severity) * 0.4), 2)

# --- SECURITY PROTECTION MIDDLEWARE ---
def login_required(role=None):
    def decorator(f):
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this secured portal.', 'danger')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Access Denied: Unauthorized Clearance Level.', 'danger')
                return redirect(url_for('user_submit'))
            return f(*args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator

# --- CONTROLLER ROUTING ---

@app.route('/', methods=['GET', 'POST'])
def user_submit():
    if request.method == 'POST':
        priority_score = calculate_priority(request.form['disaster_type'], request.form['severity'])
        new_req = HelpRequest(
            name=request.form['name'], phone=request.form['phone'], location=request.form['location'],
            disaster_type=request.form['disaster_type'], severity=int(request.form['severity']),
            priority_score=priority_score
        )
        db.session.add(new_req)
        db.session.commit()
        flash('SOS Broadcast Sent. Disaster dispatch units have updated their routing queues.', 'success')
        return redirect(url_for('user_submit'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        try:
            new_user = User(username=request.form['username'], password_hash=hashed_pw, role=request.form['role'])
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username already exists in the system database.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Session initiated. Welcome back, {user.username}.', 'success')
            return redirect(url_for('admin_dashboard' if user.role == 'Admin' else 'volunteer_panel'))
        flash('Invalid verification credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('User session securely terminated.', 'info')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required(role='Admin')
def admin_dashboard():
    requests_list = HelpRequest.query.order_by(HelpRequest.priority_score.desc(), HelpRequest.created_at.asc()).all()
    return render_template('admin.html', requests=requests_list)

@app.route('/volunteer')
@login_required(role='Volunteer')
def volunteer_panel():
    requests_list = HelpRequest.query.order_by(HelpRequest.priority_score.desc()).all()
    return render_template('volunteer.html', requests=requests_list)

@app.route('/update_status/<int:id>', methods=['POST'])
@login_required()
def update_status(id):
    req = HelpRequest.query.get_or_404(id)
    req.status = request.form['status']
    if session.get('role') == 'Volunteer':
        req.assigned_volunteer = session.get('username')
    elif 'volunteer_name' in request.form:
        req.assigned_volunteer = request.form['volunteer_name']
    db.session.commit()
    flash(f'Incident record #{id} status modified.', 'success')
    return redirect(request.referrer)

@app.route('/api/analytics')
@login_required(role='Admin')
def analytics_api():
    all_reqs = HelpRequest.query.all()
    disasters = {}
    statuses = {"Pending": 0, "In Progress": 0, "Completed": 0}
    
    for r in all_reqs:
        disasters[r.disaster_type] = disasters.get(r.disaster_type, 0) + 1
        statuses[r.status] = statuses.get(r.status, 0) + 1
        
    return jsonify({"disasters": disasters, "statuses": statuses})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Explicitly running on port 5001 to prevent Windows background port conflicts
    app.run(debug=True, port=5001)