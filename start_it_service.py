#!/usr/bin/env python3
"""
Start script for IT Service
"""
import os
import sys

# Set environment variable for IT domain
os.environ['DOMAIN_NAME'] = 'IT'

# Add services directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

from it.it_service import main

if __name__ == "__main__":
    print("Starting IT Service on port 8002...")
    main()