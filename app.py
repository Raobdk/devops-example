from flask import Flask, jsonify
import os
import requests
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

app = Flask(__name__)

# Read values from .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")

@app.route('/')
def home():
    return '✅ Flask is working. Visit /api/status for GitHub CI/CD data.'

@app.route('/api/status', methods=['GET'])
def get_github_status():
    print("📦 Checking GitHub status...")

    # Debug log for loaded environment variables
    print("🔐 GITHUB_TOKEN:", GITHUB_TOKEN[:10] + "..." if GITHUB_TOKEN else "None")
    print("👤 GITHUB_OWNER:", GITHUB_OWNER)
    print("📁 GITHUB_REPO:", GITHUB_REPO)

    # GitHub API endpoint
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs?per_page=5"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    print("🌐 Sending request to:", url)

    try:
        response = requests.get(url, headers=headers)
        print("📥 Status Code:", response.status_code)
        print("📥 Raw Response:", response.text)
    except Exception as e:
        print("❌ Request failed:", str(e))
        return jsonify({"error": "Request to GitHub API failed", "detail": str(e)}), 500

    if response.status_code != 200:
        return jsonify({
            "error": "GitHub API request failed",
            "status_code": response.status_code,
            "message": response.text
        }), 500

    try:
        runs = response.json().get("workflow_runs", [])
    except Exception as e:
        print("❌ JSON decode error:", str(e))
        return jsonify({"error": "Failed to parse GitHub API response"}), 500

    result = []
    for run in runs:
        result.append({
            "name": run.get("name", ""),
            "status": run.get("status", ""),
            "conclusion": run.get("conclusion", ""),
            "commit": run.get("head_commit", {}).get("message", ""),
            "time": run.get("updated_at", "")
        })

    print("✅ Parsed Runs:", result)
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Starting Flask Server...")
    app.run(debug=True, port=5000)
