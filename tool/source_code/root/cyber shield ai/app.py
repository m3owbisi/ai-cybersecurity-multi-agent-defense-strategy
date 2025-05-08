import os
import logging
import json
from datetime import datetime, timedelta

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-replace-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app)

# Sample data for initial display
sample_alerts = [
    {
        "id": "1",
        "title": "Potential data exfiltration detected",
        "description": "Unusual outbound traffic to unknown IP detected.",
        "severity": "critical",
        "source": "detection_agent",
        "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
        "is_resolved": False
    },
    {
        "id": "2",
        "title": "Unusual login pattern detected",
        "description": "Multiple failed login attempts followed by successful login.",
        "severity": "medium",
        "source": "detection_agent",
        "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "is_resolved": False
    },
    {
        "id": "3",
        "title": "Brute force attempt blocked",
        "description": "Multiple authentication failures from same source.",
        "severity": "high",
        "source": "defense_agent",
        "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "is_resolved": True
    }
]

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html')

@app.route('/training')
def training():
    return render_template('training.html')

# API Routes
@app.route('/api/alerts/latest')
def get_latest_alerts():
    return jsonify({
        "alerts": sample_alerts,
        "threat_level": "medium"
    })

@app.route('/api/status')
def get_system_status():
    return jsonify({
        "status": "active",
        "agents": {
            "defense": {"status": "active", "capabilities": ["vulnerability_assessment", "countermeasures"]},
            "offense": {"status": "active", "capabilities": ["simulation", "penetration_testing"]},
            "detection": {"status": "active", "capabilities": ["traffic_analysis", "anomaly_detection"]},
            "coordinator": {"status": "active", "capabilities": ["orchestration", "workflow_management"]}
        },
        "system_health": 92.5
    })

logger.info("Cybersecurity AI Platform initialized")
