#!/usr/bin/env python3
"""
Generic script to start any domain service
Usage: python start_domain_service.py <domain_name> [port]
Example: python start_domain_service.py finance 8003
"""
import os
import sys
import argparse

# Add services directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

from common.domain_factory import create_service_for_domain, DomainServiceFactory


def main():
    parser = argparse.ArgumentParser(description='Start a domain-specific service')
    parser.add_argument('domain', type=str, help='Domain name (e.g., hr, it, finance, etc.)')
    parser.add_argument('--port', type=int, help='Port number (optional, will use default if not specified)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address (default: 0.0.0.0)')
    parser.add_argument('--list-domains', action='store_true', help='List available domains')
    
    args = parser.parse_args()
    
    # List available domains
    if args.list_domains:
        print("Available domains:")
        domains = DomainServiceFactory.get_available_domains()
        for domain in domains:
            print(f"  - {domain}")
        return
    
    # Set environment variable for domain
    domain_name = args.domain.upper()
    os.environ['DOMAIN_NAME'] = domain_name
    
    # Create and run the service
    print(f"Starting {domain_name} Service...")
    if args.port:
        print(f"Port: {args.port}")
    else:
        print("Port: Using default for domain")
    
    service = create_service_for_domain(args.domain, args.port)
    service.run()


if __name__ == "__main__":
    main()