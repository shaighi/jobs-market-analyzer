from flask import Flask, render_template_string, jsonify, request
import json

app = Flask(__name__)

# MOCK DATA (no pandas needed!)
mock_jobs = [
    {'title': 'Python Developer', 'company': 'TCS', 'location': 'Karachi', 'salary': '80000', 'description': 'Python Django 2+ years'},
    {'title': 'JavaScript Developer', 'company': 'Sapient', 'location': 'Lahore', 'salary': '75000', 'description': 'React Node.js 3+ years'},
    {'title': 'Data Analyst', 'company': 'Jazz', 'location': 'Islamabad', 'salary': '70000', 'description': 'SQL Python analytics'},
    {'title': 'Java Developer', 'company': '10Pearls', 'location': 'Karachi', 'salary': '85000', 'description': 'Spring Boot Java'},
    {'title': 'Full Stack Developer', 'company': 'TCS', 'location': 'Lahore', 'salary': '90000', 'description': 'Python React SQL'},
    {'title': 'Frontend Developer', 'company': 'Karachi Electric', 'location': 'Karachi', 'salary': '0', 'description': 'React CSS JavaScript'},
    {'title': 'DevOps Engineer', 'company': 'Sapient', 'location': 'Islamabad', 'salary': '95000', 'description': 'AWS Docker Linux'},
    {'title': 'Database Admin', 'company': 'Jazz', 'location': 'Lahore', 'salary': '70000', 'description': 'SQL MongoDB'},
    {'title': 'Mobile Developer', 'company': '10Pearls', 'location': 'Karachi', 'salary': '80000', 'description': 'React Native JavaScript'},
    {'title': 'AI Engineer', 'company': 'TCS', 'location': 'Islamabad', 'salary': '100000', 'description': 'Python TensorFlow ML'},
]

def get_top_skills():
    skills = ['Python', 'JavaScript', 'Java', 'SQL', 'React', 'Django', 'Node.js', 'AWS', 'Docker']
    skill_count = {}
    for job in mock_jobs:
        for skill in skills:
            if skill.lower() in job['description'].lower():
                skill_count[skill] = skill_count.get(skill, 0) + 1
    return dict(sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10])

def get_companies():
    companies = {}
    for job in mock_jobs:
        companies[job['company']] = companies.get(job['company'], 0) + 1
    return companies

def get_locations():
    locations = {}
    for job in mock_jobs:
        locations[job['location']] = locations.get(job['location'], 0) + 1
    return locations

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
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            header { text-align: center; color: white; margin-bottom: 30px; }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            .btn-section { text-align: center; margin: 20px 0; }
            button { 
                background: #ff6b6b; 
                color: white; 
                padding: 12px 30px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 1em;
                font-weight: bold;
            }
            button:hover { background: #ff5252; }
            .card { background: white; padding: 20px; border-radius: 10px; margin: 15px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
            .stat-box { background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; border-left: 4px solid #667eea; }
            .stat-number { font-size: 2em; color: #667eea; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Pakistani Job Market Analyzer</h1>
                <p>Real-time job insights from Rozee.pk</p>
            </header>
            
            <div class="btn-section">
                <button onclick="loadData()">📊 LOAD DASHBOARD</button>
            </div>
            
            <div class="card">
                <h2>📈 Statistics</h2>
                <div class="stats" id="stats">
                    <div class="stat-box">
                        <div class="stat-number" id="total-jobs">-</div>
                        <div>Total Jobs</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="companies-count">-</div>
                        <div>Companies</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="locations-count">-</div>
                        <div>Cities</div>
                    </div>
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
        
        <script>
            function loadData() {
                // Stats
                fetch('/api/stats')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('total-jobs').textContent = data.total;
                        document.getElementById('companies-count').textContent = data.companies;
                        document.getElementById('locations-count').textContent = data.locations;
                    });
                
                // Skills
                fetch('/api/skills')
                    .then(r => r.json())
                    .then(data => {
                        const skills = Object.keys(data);
                        const counts = Object.values(data);
                        Plotly.newPlot('skills-chart', [{x: skills, y: counts, type: 'bar', marker: {color: '#667eea'}}], {margin: {b: 100}}, {responsive: true});
                    });
                
                // Companies
                fetch('/api/companies')
                    .then(r => r.json())
                    .then(data => {
                        const companies = Object.keys(data);
                        const counts = Object.values(data);
                        Plotly.newPlot('companies-chart', [{x: counts, y: companies, type: 'bar', orientation: 'h', marker: {color: '#764ba2'}}], {margin: {l: 150}}, {responsive: true});
                    });
                
                // Locations
                fetch('/api/locations')
                    .then(r => r.json())
                    .then(data => {
                        const locations = Object.keys(data);
                        const counts = Object.values(data);
                        Plotly.newPlot('locations-chart', [{labels: locations, values: counts, type: 'pie'}], {}, {responsive: true});
                    });
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/stats')
def stats():
    return jsonify({
        'total': len(mock_jobs),
        'companies': len(get_companies()),
        'locations': len(get_locations())
    })

@app.route('/api/skills')
def skills():
    return jsonify(get_top_skills())

@app.route('/api/companies')
def companies():
    return jsonify(get_companies())

@app.route('/api/locations')
def locations():
    return jsonify(get_locations())

if __name__ == '__main__':
    app.run(debug=True)
    
