#!/usr/bin/env python3
"""
FairClaimRCM CLI Tool

Command-line interface for testing and interacting with FairClaimRCM.
"""

import argparse
import json
import sys
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

def analyze_text(text, claim_id=None):
    """Analyze clinical text and get coding recommendations."""
    url = f"{BASE_URL}/api/v1/coding/analyze"
    
    data = {
        "clinical_text": text,
        "claim_id": claim_id,
        "include_explanations": True
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print("Coding Recommendations:")
            print("=" * 50)
            
            for rec in result['recommendations']:
                print(f"\n{rec['code_type']} Code: {rec['code']}")
                print(f"Confidence: {rec['confidence_score']:.1%}")
                print(f"Source: {rec['recommendation_source']}")
                print(f"Reasoning: {rec['reasoning']}")
            
            print(f"\nSummary: {json.dumps(result['summary'], indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to FairClaimRCM API. Is the server running?")

def validate_codes(icd10=None, cpt=None, drg=None):
    """Validate medical codes."""
    url = f"{BASE_URL}/api/v1/coding/validate"
    
    codes = {}
    if icd10:
        codes['icd10'] = icd10.split(',')
    if cpt:
        codes['cpt'] = cpt.split(',')
    if drg:
        codes['drg'] = drg.split(',')
    
    try:
        response = requests.post(url, json=codes)
        if response.status_code == 200:
            result = response.json()
            print("Code Validation Results:")
            print("=" * 50)
            
            for code_type, results in result.items():
                if code_type != 'overall_valid' and results:
                    print(f"\n{code_type.upper()} Codes:")
                    for res in results:
                        status = "✅ Valid" if res['valid'] else "❌ Invalid"
                        print(f"  {res['code']}: {status}")
                        if res['valid']:
                            print(f"    Description: {res['description']}")
                        else:
                            print(f"    Error: {res['error']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to FairClaimRCM API. Is the server running?")

def search_codes(system, query):
    """Search terminology codes."""
    url = f"{BASE_URL}/api/v1/terminology/{system}/search"
    params = {"q": query, "limit": 10}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            print(f"Search Results for '{query}' in {system.upper()}:")
            print("=" * 50)
            
            for item in result['results']:
                if system == 'drg':
                    print(f"  {item['drg_code']}: {item['description']}")
                else:
                    print(f"  {item['code']}: {item['description']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to FairClaimRCM API. Is the server running?")

def health_check():
    """Check API health."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API is healthy: {result['status']}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to FairClaimRCM API")

def main():
    parser = argparse.ArgumentParser(
        description="FairClaimRCM CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze "Patient presents with chest pain and shortness of breath"
  %(prog)s validate --icd10 "I21.9,J44.1" --cpt "99213"
  %(prog)s search icd10 "myocardial"
  %(prog)s health
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze clinical text')
    analyze_parser.add_argument('text', help='Clinical text to analyze')
    analyze_parser.add_argument('--claim-id', help='Optional claim ID')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate medical codes')
    validate_parser.add_argument('--icd10', help='Comma-separated ICD-10 codes')
    validate_parser.add_argument('--cpt', help='Comma-separated CPT codes')
    validate_parser.add_argument('--drg', help='Comma-separated DRG codes')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search terminology codes')
    search_parser.add_argument('system', choices=['icd10', 'cpt', 'drg'], help='Code system to search')
    search_parser.add_argument('query', help='Search query')
    
    # Health command
    subparsers.add_parser('health', help='Check API health')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'analyze':
        analyze_text(args.text, args.claim_id)
    elif args.command == 'validate':
        if not any([args.icd10, args.cpt, args.drg]):
            print("Error: At least one code type must be specified")
            return
        validate_codes(args.icd10, args.cpt, args.drg)
    elif args.command == 'search':
        search_codes(args.system, args.query)
    elif args.command == 'health':
        health_check()

if __name__ == "__main__":
    main()
