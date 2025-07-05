#!/usr/bin/env python3
"""
Start both HR and IT services
"""
import subprocess
import sys
import time
import os
from concurrent.futures import ThreadPoolExecutor
import signal

# Store subprocess references for cleanup
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down services...")
    for p in processes:
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def start_service(service_name, script_name, port):
    """Start a service and monitor its output"""
    print(f"Starting {service_name} on port {port}...")
    
    # Start the service
    process = subprocess.Popen(
        [sys.executable, script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    processes.append(process)
    
    # Monitor output
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"[{service_name}] {line.strip()}")
    
    return process

def main():
    """Main function to start all services"""
    print("Starting all services...")
    print("HR Service will run on http://localhost:8001")
    print("IT Service will run on http://localhost:8002")
    print("\nPress Ctrl+C to stop all services\n")
    
    # Use thread pool to start services concurrently
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both services to run concurrently
        hr_future = executor.submit(start_service, "HR", "start_hr_service.py", 8001)
        it_future = executor.submit(start_service, "IT", "start_it_service.py", 8002)
        
        # Wait for both to complete (they won't unless there's an error)
        try:
            hr_future.result()
            it_future.result()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()