#!/usr/bin/env python3
"""
Migration script to help transition from single service to domain-separated services
"""
import os
import shutil
import sys

def create_backup():
    """Create a backup of the main.py file"""
    if os.path.exists('main.py'):
        backup_name = 'main.py.backup'
        counter = 1
        while os.path.exists(backup_name):
            backup_name = f'main.py.backup.{counter}'
            counter += 1
        shutil.copy('main.py', backup_name)
        print(f"Created backup: {backup_name}")
        return backup_name
    return None

def check_environment():
    """Check if the environment is ready for migration"""
    issues = []
    
    # Check if services directory exists
    if not os.path.exists('services'):
        issues.append("Services directory not found. Please ensure you have the new service files.")
    
    # Check for required files
    required_files = [
        'services/common/base_service.py',
        'services/hr/hr_service.py',
        'services/it/it_service.py',
        'start_hr_service.py',
        'start_it_service.py',
        'start_all_services.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            issues.append(f"Required file missing: {file}")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("Creating .env from .env.example...")
            shutil.copy('.env.example', '.env')
            print("Please edit .env with your configuration")
        else:
            issues.append("No .env file found. Please create one based on .env.example")
    
    return issues

def update_nginx_config():
    """Generate nginx configuration for the new services"""
    nginx_config = """# Nginx configuration for HR and IT services

upstream hr_service {
    server localhost:8001;
}

upstream it_service {
    server localhost:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    # Route based on path prefix
    location /hr/ {
        proxy_pass http://hr_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /it/ {
        proxy_pass http://it_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Default route (you can change this)
    location / {
        proxy_pass http://it_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    
    with open('nginx_services.conf', 'w') as f:
        f.write(nginx_config)
    print("Created nginx_services.conf - Please review and adapt to your needs")

def create_systemd_services():
    """Create systemd service files for production deployment"""
    hr_service = """[Unit]
Description=HR FastAPI Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/python start_hr_service.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    it_service = """[Unit]
Description=IT FastAPI Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/python start_it_service.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('hr-service.service', 'w') as f:
        f.write(hr_service)
    
    with open('it-service.service', 'w') as f:
        f.write(it_service)
    
    print("Created systemd service files: hr-service.service and it-service.service")
    print("Edit the paths and copy to /etc/systemd/system/ for production deployment")

def main():
    """Main migration function"""
    print("=== Migration to Domain-Separated Services ===\n")
    
    # Step 1: Check environment
    print("Step 1: Checking environment...")
    issues = check_environment()
    if issues:
        print("\nFound issues that need to be resolved:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    print("✓ Environment check passed\n")
    
    # Step 2: Create backup
    print("Step 2: Creating backup...")
    backup_file = create_backup()
    if backup_file:
        print(f"✓ Backup created: {backup_file}\n")
    else:
        print("✓ No main.py found to backup (fresh installation)\n")
    
    # Step 3: Generate configurations
    print("Step 3: Generating configuration files...")
    update_nginx_config()
    create_systemd_services()
    print("✓ Configuration files generated\n")
    
    # Step 4: Instructions
    print("=== Migration Complete ===\n")
    print("Next steps:")
    print("1. Review and update .env file with your configuration")
    print("2. Install new dependencies: pip install -r requirements.txt")
    print("3. Test the services:")
    print("   - Option 1: python start_all_services.py")
    print("   - Option 2: docker-compose up")
    print("4. Update your client applications to use:")
    print("   - HR endpoints: http://localhost:8001")
    print("   - IT endpoints: http://localhost:8002")
    print("\nFor production deployment:")
    print("- Review nginx_services.conf for reverse proxy setup")
    print("- Use the systemd service files for automatic startup")
    print("\nRefer to README_SERVICES.md for detailed documentation")

if __name__ == "__main__":
    main()