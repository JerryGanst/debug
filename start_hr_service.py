#!/usr/bin/env python3
"""
Start script for HR Service
"""
import os
import sys

# Set environment variable for HR domain
os.environ['DOMAIN_NAME'] = 'HR'

# Add services directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

from hr.hr_service import main

if __name__ == "__main__":
    print("Starting HR Service on port 8001...")
    main()