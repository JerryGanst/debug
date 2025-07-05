#!/usr/bin/env python3
"""
Start multiple domain services dynamically
"""
import subprocess
import sys
import time
import os
from concurrent.futures import ThreadPoolExecutor
import signal
import argparse
from typing import List, Tuple

# Store subprocess references for cleanup
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down services...")
    for p in processes:
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def start_service(domain_name: str, port: int):
    """Start a domain service and monitor its output"""
    print(f"Starting {domain_name.upper()} service on port {port}...")
    
    # Start the service using the generic domain starter
    cmd = [sys.executable, "start_domain_service.py", domain_name, "--port", str(port)]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    processes.append(process)
    
    # Monitor output
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"[{domain_name.upper()}] {line.strip()}")
    
    return process

def start_embedding_service():
    """Start the embedding service"""
    print("Starting Embedding Service on port 8100...")
    
    process = subprocess.Popen(
        [sys.executable, "embedding_service_api/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    processes.append(process)
    
    # Monitor output
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"[EMBEDDING] {line.strip()}")
    
    return process

def parse_domain_config(config_str: str) -> Tuple[str, int]:
    """Parse domain configuration string (format: domain:port)"""
    parts = config_str.split(':')
    if len(parts) != 2:
        raise ValueError(f"Invalid domain config: {config_str}. Use format: domain:port")
    
    domain = parts[0]
    try:
        port = int(parts[1])
    except ValueError:
        raise ValueError(f"Invalid port number: {parts[1]}")
    
    return domain, port

def main():
    """Main function to start all services"""
    parser = argparse.ArgumentParser(description='Start multiple domain services')
    parser.add_argument('domains', nargs='*', 
                       help='Domain configurations (format: domain:port)',
                       default=['hr:8001', 'it:8002'])
    parser.add_argument('--no-embedding', action='store_true',
                       help='Skip starting the embedding service')
    
    args = parser.parse_args()
    
    # Parse domain configurations
    domains = []
    for config in args.domains:
        try:
            domain, port = parse_domain_config(config)
            domains.append((domain, port))
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    print("Starting all services...")
    print(f"Configured domains: {', '.join([f'{d[0].upper()} (port {d[1]})' for d in domains])}")
    if not args.no_embedding:
        print("Embedding Service will run on http://localhost:8100")
    print("\nPress Ctrl+C to stop all services\n")
    
    # Calculate number of workers needed
    num_workers = len(domains) + (0 if args.no_embedding else 1)
    
    # Use thread pool to start services concurrently
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        
        # Start embedding service if not disabled
        if not args.no_embedding:
            futures.append(executor.submit(start_embedding_service))
        
        # Start domain services
        for domain, port in domains:
            futures.append(executor.submit(start_service, domain, port))
        
        # Wait for all services (they won't complete unless there's an error)
        try:
            for future in futures:
                future.result()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()