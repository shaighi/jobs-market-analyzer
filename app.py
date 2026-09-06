from flask import Flask, render_template_string, jsonify, request
import pandas as pd
import json

app = Flask(__name__)

csv_file = 'jobs.csv'

# MOCK DATA
def create_mock_data():
    mock_jobs = [
        {'title': 'Python Developer', 'company': 'TCS', 'location': 'Karachi', 'salary': '80000', 'description': 'Python Django 2+ years'},
        {'title': 'JavaScript Developer', 'company': 'Sapient', 'location': 'Lahore', 'salary': '75000', 'description': 'React Node.js 3+ years'},
        {'title': 'Data Analyst', 'company': 'Jazz', 'location': 'Islamabad', 'salary': '70000', 'description': 'SQL Python analytics'},
        {'title': 'Java Developer', 'company': '10Pearls', 'location': 'Karachi', 'salary': '85000', 'description': 'Spring Boot Java 8'},
        {'title': 'Full Stack Developer', 'company': 'TCS', 'location': 'Lahore', 'salary': '90000', 'description': 'Python React SQL'},
        {'title': 'Frontend Developer', 'company': 'Karachi Electric', 'location': 'Karachi', 'salary': '0', 'description': 'React CSS JavaScript'},
        {'title': 'DevOps Engineer', 'company': 'Sapient', 'location': 'Islamabad', 'salary': '95000', 'description': 'AWS Docker Linux'},
        {'title': 'Database Admin', 'company': 'Jazz', 'location': 'Lahore', 'salary': '70000', 'description': 'SQL MongoDB'},
        {'title': 'Mobile Developer', 'company': '10Pearls', 'location': 'Karachi', 'salary': '80000', 'description': 'React Native JavaScript'},
        {'title': 'AI Engineer', 'company': 'TCS', 'location': 'Islamabad', 'salary': '100000', 'description': 'Python TensorFlow ML'},
    ]
    
    df = pd.DataFrame(mock_jobs)
    df.to_csv(csv_file, index=False)

def load_data():
    try:
        return pd.read_csv(csv_file)
    except:
        return None

def get_top_skills(df, top_n=10):
    skills = ['Python', 'JavaScript', 'Java', 'SQL', 'React', 'Django', 
              'Node.js', 'Angular', 'AWS', 'Docker', 'TensorFlow', 'MongoDB', 'Linux']
    skill_count = {}
    
    for desc in df['description'].fillna(''):
        for skill in skills:
            if skill.lower() in desc.lower():
                skill_count[skill] = skill_count.get(skill, 0) + 1
    
    return dict(sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:top_n])

def match_resume(user_skills):
    """Resume ko jobs se match karo"""
    df = load_data()
    if df is None:
        return []
    
    matches = []
    user_skills_lower = [s.lower() for s in user_skills]
    
    for idx, job in df.iterrows():
        desc_lower = job['description'].lower()
        match_count = sum(1 for skill in user_skills_lower if skill in desc_lower)
        match_percentage = (match_count / len(user_skills_lower) * 100) if user_skills_lower else 0
        
        if match_percentage > 0:
            matches.append({
                'title': job['title'],
                'company': job['company'],
                'match': int(match_percentage),
                'salary': job['salary']
            })
    
    return sorted(matches, key=lambda x: x['match'], reverse=True)

def predict_salary(job_title, location, experience_years):
    """Salary predict karo"""
    df = load_data()
    if df is None:
        return 0
    
    # Base salaries
    base_salaries = {
        'developer': 75000,
        'engineer': 80000,
        'analyst': 65000,
        'admin': 60000,
        'manager': 90000
    }
    
    # Location multiplier
    location_multiplier = {
        'karachi': 1.0,
        'lahore': 0.95,
        'islamabad': 1.05,
        'peshawar': 0.85
    }
    
    # Find base salary
    base = 70000
    for role, salary in base_salaries.items():
        if role in job_title.lower():
            base = salary
            break
    
    # Apply location multiplier
    location_lower = location.lower()
    multiplier = location_multiplier.get(location_lower, 1.0)
    
    # Apply experience
    experience_bonus = experience_years * 5000
    
    final_salary = int((base * multiplier) + experience_bonus)
    return final_salary

@app.route('/')
def dashboard():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pakistani Job Market Analyzer</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            header { text-align: center; color: white; margin-bottom: 30px; }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            .subtitle { font-size: 1.1em; opacity: 0.9; }
            .tabs { display: flex; gap: 10px; justify-content: center; margin: 20px 0; flex-wrap: wrap; }
            .tab-btn { 
                background: white; 
                color: #667eea;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                transition: 0.3s;
            }
            .tab-btn.active { background: #ff6b6b; color: white; }
            .tab-btn:hover { transform: translateY(-2px); }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .card { background: white; padding: 20px; border-radius: 10px; margin: 15px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
            .stat-box { background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; border-left: 4px solid #667eea; }
            .stat-number { font-size: 2em; color: #667eea; font-weight: bold; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            input, select { 
                width: 100%; 
                padding: 10px; 
                border: 1px solid #ddd; 
                border-radius: 5px;
                font-size: 1em;
            }
            button { 
                background: #ff6b6b; 
                color: white; 
                padding: 12px 30px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 1em;
                font-weight: bold;
                margin-top: 10px;
            }
            button:hover { background: #ff5252; }
            .result-item { 
                background: #f9f9f9; 
                padding: 15px; 
                border-left: 4px solid #667eea;
                margin: 10px 0;
                border-radius: 5px;
            }
            .match-score { 
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-weight: bold;
                margin-top: 10px;
            }
            .salary-result { 
                font-size: 1.5em; 
                color: #667eea; 
                font-weight: bold;
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Pakistani Job Market Analyzer</h1>
                <p class="subtitle">Complete Job Analytics Platform</p>
            </header>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('dashboard')">📈 Dashboard</button>
                <button class="tab-btn" onclick="switchTab('matcher')">🎯 Resume Matcher</button>
                <button class="tab-btn" onclick="switchTab('salary')">💰 Salary Predictor</button>
            </div>
            
            <!-- Dashboard Tab -->
            <div id="dashboard" class="tab-content active">
                <div class="card">
                    <h2>📊 Load Dashboard</h2>
                    <button onclick="loadDashboard()">🔄 LOAD DATA</button>
                </div>
                
                <div class="card">
                    <h2>📈 Statistics</h2>
                    <div class="stats" id="stats">
                        <div class="stat-box"><div class="stat-number">-</div><div>Total Jobs</div></div>
                        <div class="stat-box"><div class="stat-number">-</div><div>With Salary</div></div>
                        <div class="stat-box"><div class="stat-number">-</div><div>Cities</div></div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🔥 Top Skills in Demand</h2>
                    <div id="skills-chart"></div>
                </div>
                
                <div class="card">
                    <h2>💼 Top Companies</h2>
                    <div id="companies-chart"></div>
                </div>
                
                <div class="card">
                    <h2>🌍 Jobs by Location</h2>
                    <div id="locations-chart"></div>
                </div>
            </div>
            
            <!-- Resume Matcher Tab -->
            <div id="matcher" class="tab-content">
                <div class="card">
                    <h2>🎯 Resume Matcher</h2>
                    <p>Enter your skills (comma-separated) to find matching jobs:</p>
                    <div class="form-group">
                        <label>Your Skills:</label>
                        <input type="text" id="user-skills" placeholder="e.g., Python, React, SQL">
                    </div>
                    <button onclick="matchResume()">🔍 Find Matching Jobs</button>
                    <div id="match-results"></div>
                </div>
            </div>
            
            <!-- Salary Predictor Tab -->
            <div id="salary" class="tab-content">
                <div class="card">
                    <h2>💰 Salary Predictor</h2>
                    <p>Predict your salary based on job title, location, and experience:</p>
                    
                    <div class="form-group">
                        <label>Job Title:</label>
                        <input type="text" id="job-title" placeholder="e.g., Python Developer">
                    </div>
                    
                    <div class="form-group">
                        <label>Location:</label>
                        <select id="location">
                            <option>Karachi</option>
                            <option>Lahore</option>
                            <option>Islamabad</option>
                            <option>Peshawar</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Experience (years):</label>
                        <input type="number" id="experience" min="0" max="50" placeholder="e.g., 3">
                    </div>
                    
                    <button onclick="predictSalary()">💹 Predict Salary</button>
                    <div id="salary-result"></div>
                </div>
            </div>
        </div>
        
        <script>
            function switchTab(tab) {
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tab).classList.add('active');
                event.target.classList.add('active');
            }
            
            function loadDashboard() {
                fetch('/api/stats')
                    .then(res => res.json())
                    .then(data => {
                        const html = `
                            <div class="stat-box">
                                <div class="stat-number">${data.total}</div>
                                <div>Total Jobs</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-number">${data.with_salary}</div>
                                <div>With Salary</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-number">${data.locations}</div>
                                <div>Cities</div>
                            </div>
                        `;
                        document.getElementById('stats').innerHTML = html;
                    });
                
                fetch('/api/skills')
                    .then(res => res.json())
                    .then(data => {
                        const skills = Object.keys(data);
                        const counts = Object.values(data);
                        const trace = { x: skills, y: counts, type: 'bar', marker: {color: '#667eea'} };
                        Plotly.newPlot('skills-chart', [trace], {margin: {b: 100}, xaxis: {tickangle: -45}}, {responsive: true});
                    });
                
                fetch('/api/companies')
                    .then(res => res.json())
                    .then(data => {
                        const companies = Object.keys(data);
                        const counts = Object.values(data);
                        const trace = { x: counts, y: companies, type: 'bar', orientation: 'h', marker: {color: '#764ba2'} };
                        Plotly.newPlot('companies-chart', [trace], {margin: {l: 150}}, {responsive: true});
                    });
                
                fetch('/api/locations')
                    .then(res => res.json())
                    .then(data => {
                        const locations = Object.keys(data);
                        const counts = Object.values(data);
                        const trace = { labels: locations, values: counts, type: 'pie' };
                        Plotly.newPlot('locations-chart', [trace], {}, {responsive: true});
                    });
            }
            
            function matchResume() {
                const skills = document.getElementById('user-skills').value;
                fetch('/api/match-resume', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({skills: skills})
                })
                .then(res => res.json())
                .then(data => {
                    let html = '<h3>Matching Jobs:</h3>';
                    if (data.length === 0) {
                        html += '<p>No matches found</p>';
                    } else {
                        data.forEach(job => {
                            html += `
                                <div class="result-item">
                                    <strong>${job.title}</strong><br>
                                    Company: ${job.company}<br>
                                    Salary: Rs. ${job.salary || 'Not mentioned'}<br>
                                    <span class="match-score">${job.match}% Match</span>
                                </div>
                            `;
                        });
                    }
                    document.getElementById('match-results').innerHTML = html;
                });
            }
            
            function predictSalary() {
                const jobTitle = document.getElementById('job-title').value;
                const location = document.getElementById('location').value;
                const experience = document.getElementById('experience').value;
                
                fetch('/api/predict-salary', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({job_title: jobTitle, location: location, experience: experience})
                })
                .then(res => res.json())
                .then(data => {
                    const html = `
                        <div class="result-item">
                            <h3>Estimated Monthly Salary</h3>
                            <div class="salary-result">Rs. ${data.salary.toLocaleString()}</div>
                            <small>Based on: ${jobTitle} in ${location} with ${experience} years experience</small>
                        </div>
                    `;
                    document.getElementById('salary-result').innerHTML = html;
                });
            }
            
            // Load dashboard on page load
            window.onload = () => loadDashboard();
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/stats')
def stats_api():
    df = load_data()
    if df is None:
        return jsonify({'total': 0, 'with_salary': 0, 'locations': 0})
    return jsonify({
        'total': len(df),
        'with_salary': len(df[df['salary'] != '0']),
        'locations': df['location'].nunique()
    })

@app.route('/api/skills')
def skills_api():
    df = load_data()
    if df is None:
        return jsonify({})
    return jsonify(get_top_skills(df, 10))

@app.route('/api/companies')
def companies_api():
    df = load_data()
    if df is None:
        return jsonify({})
    top_companies = df['company'].value_counts().head(10)
    return jsonify(top_companies.to_dict())

@app.route('/api/locations')
def locations_api():
    df = load_data()
    if df is None:
        return jsonify({})
    locations = df['location'].value_counts()
    return jsonify(locations.to_dict())

@app.route('/api/match-resume', methods=['POST'])
def match_resume_api():
    data = request.json
    skills = [s.strip() for s in data.get('skills', '').split(',')]
    matches = match_resume(skills)
    return jsonify(matches)

@app.route('/api/predict-salary', methods=['POST'])
def predict_salary_api():
    data = request.json
    job_title = data.get('job_title', '')
    location = data.get('location', '')
    experience = int(data.get('experience', 0))
    
    salary = predict_salary(job_title, location, experience)
    return jsonify({'salary': salary})

if __name__ == '__main__':
    create_mock_data()
    print("🚀 Go to: http://localhost:5000")
    app.run(debug=True)
    