#!/usr/bin/env python3
"""
Deployment helper script for Face Recognition API
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_requirements():
    """Check if all required files exist"""
    print("🔍 Checking deployment requirements...")
    
    required_files = [
        "face_recognition_api.py",
        "requirements.txt", 
        "Procfile",
        "Dockerfile",
        "railway.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check if dataset exists
    if not Path("dataset/images").exists():
        print("⚠️  Warning: dataset/images directory not found")
        print("   Your API will work but won't have face recognition data")
    
    print("✅ All deployment files are ready")
    return True

def setup_git():
    """Initialize git repository if needed"""
    print("🔧 Setting up Git repository...")
    
    if not Path(".git").exists():
        run_command("git init", "Initializing Git repository")
        run_command("git branch -M main", "Setting main branch")
    
    # Create .gitignore if it doesn't exist
    gitignore_content = """
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Local files
extracted_frames/
*.mp4
*.avi
test_result.png
face_encodings.pkl
face_model.yml
*_labels.pkl

# Environment variables
.env
"""
    
    if not Path(".gitignore").exists():
        with open(".gitignore", "w") as f:
            f.write(gitignore_content.strip())
        print("✅ Created .gitignore file")

def prepare_for_deployment():
    """Prepare the project for deployment"""
    print("📦 Preparing project for deployment...")
    
    # Add all files to git
    run_command("git add .", "Adding files to Git")
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        run_command('git commit -m "Prepare for deployment"', "Committing changes")
    else:
        print("✅ No changes to commit")

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚂 Deploying to Railway...")
    print("📋 Instructions for Railway deployment:")
    print("1. Go to https://railway.app")
    print("2. Sign up/login with GitHub")
    print("3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. Select your repository")
    print("5. Railway will automatically deploy your app!")
    print("\n🔗 After deployment, your API will be available at:")
    print("   https://your-app-name.railway.app/api/health")

def deploy_to_render():
    """Deploy to Render"""
    print("🎨 Deploying to Render...")
    print("📋 Instructions for Render deployment:")
    print("1. Go to https://render.com")
    print("2. Sign up/login with GitHub")
    print("3. Click 'New' → 'Web Service'")
    print("4. Connect your GitHub repository")
    print("5. Configure:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn --bind 0.0.0.0:$PORT face_recognition_api:app")
    print("6. Click 'Create Web Service'")

def deploy_to_heroku():
    """Deploy to Heroku"""
    print("🟣 Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    result = subprocess.run("heroku --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ Heroku CLI not installed")
        print("📥 Install from: https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    print("📋 Heroku deployment steps:")
    app_name = input("Enter your Heroku app name (or press Enter to auto-generate): ").strip()
    
    if app_name:
        run_command(f"heroku create {app_name}", f"Creating Heroku app '{app_name}'")
    else:
        run_command("heroku create", "Creating Heroku app with auto-generated name")
    
    run_command("git push heroku main", "Deploying to Heroku")
    run_command("heroku open", "Opening deployed app")

def test_local_deployment():
    """Test the API locally before deployment"""
    print("🧪 Testing API locally...")
    
    # Install dependencies
    run_command("pip install -r requirements.txt", "Installing dependencies")
    
    print("🚀 Starting local server for testing...")
    print("📝 The server will start on http://localhost:5000")
    print("🔍 Test endpoints:")
    print("   - Health: http://localhost:5000/api/health")
    print("   - Load dataset: POST http://localhost:5000/api/load-dataset")
    print("\n⏹️  Press Ctrl+C to stop the server when done testing")
    
    try:
        subprocess.run([sys.executable, "face_recognition_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n✅ Local testing completed")

def main():
    """Main deployment workflow"""
    print("🌍 Face Recognition API - Global Deployment Helper")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("❌ Please fix the missing requirements before deployment")
        return
    
    # Setup git
    setup_git()
    
    print("\n🚀 Choose deployment option:")
    print("1. 🧪 Test locally first")
    print("2. 🚂 Deploy to Railway (Recommended - Free)")
    print("3. 🎨 Deploy to Render (Free)")
    print("4. 🟣 Deploy to Heroku (Paid)")
    print("5. 📦 Just prepare for manual deployment")
    print("6. ❌ Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        test_local_deployment()
    elif choice == "2":
        prepare_for_deployment()
        deploy_to_railway()
    elif choice == "3":
        prepare_for_deployment()
        deploy_to_render()
    elif choice == "4":
        prepare_for_deployment()
        deploy_to_heroku()
    elif choice == "5":
        prepare_for_deployment()
        print("✅ Project prepared for deployment")
        print("📖 See DEPLOYMENT_GUIDE.md for manual deployment instructions")
    elif choice == "6":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
