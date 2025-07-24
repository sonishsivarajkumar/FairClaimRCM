"""
Basic API Usage Example for FairClaimRCM

This script demonstrates how to use the FairClaimRCM API for:
- Creating claims
- Getting coding recommendations
- Validating codes
- Retrieving audit information
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

def create_sample_claim():
    """Create a sample claim for testing."""
    url = f"{BASE_URL}/api/v1/claims/"
    
    claim_data = {
        "claim_id": f"CLAIM-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "patient_id": "PATIENT-12345",
        "encounter_id": "ENC-67890",
        "chief_complaint": "Chest pain and shortness of breath",
        "history_present_illness": "65-year-old male presents with acute onset chest pain radiating to left arm, associated with shortness of breath and diaphoresis. Pain started 2 hours ago while at rest.",
        "discharge_summary": "Patient admitted with acute myocardial infarction. Underwent cardiac catheterization with stent placement. Stable condition at discharge on dual antiplatelet therapy."
    }
    
    response = requests.post(url, json=claim_data)
    
    if response.status_code == 201:
        print("✅ Claim created successfully!")
        claim = response.json()
        print(f"   Claim ID: {claim['claim_id']}")
        return claim
    else:
        print(f"❌ Failed to create claim: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def get_coding_recommendations(clinical_text, claim_id=None):
    """Get coding recommendations for clinical text."""
    url = f"{BASE_URL}/api/v1/coding/analyze"
    
    coding_request = {
        "clinical_text": clinical_text,
        "claim_id": claim_id,
        "include_explanations": True
    }
    
    response = requests.post(url, json=coding_request)
    
    if response.status_code == 200:
        print("✅ Coding recommendations generated!")
        recommendations = response.json()
        
        print(f"   Total recommendations: {len(recommendations['recommendations'])}")
        print(f"   Summary: {recommendations['summary']}")
        
        for i, rec in enumerate(recommendations['recommendations'][:3], 1):
            print(f"\n   {i}. {rec['code_type']} Code: {rec['code']}")
            print(f"      Confidence: {rec['confidence_score']:.1%}")
            print(f"      Source: {rec['recommendation_source']}")
            print(f"      Reasoning: {rec['reasoning'][:100]}...")
        
        return recommendations
    else:
        print(f"❌ Failed to get recommendations: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def validate_codes(codes):
    """Validate a set of medical codes."""
    url = f"{BASE_URL}/api/v1/coding/validate"
    
    response = requests.post(url, json=codes)
    
    if response.status_code == 200:
        validation_result = response.json()
        print("✅ Code validation completed!")
        print(f"   Overall valid: {validation_result['overall_valid']}")
        
        for code_type, results in validation_result.items():
            if code_type != 'overall_valid' and results:
                print(f"\n   {code_type.upper()} Codes:")
                for result in results:
                    status = "✅" if result['valid'] else "❌"
                    print(f"     {status} {result['code']}: {result.get('description', result.get('error', 'N/A'))}")
        
        return validation_result
    else:
        print(f"❌ Failed to validate codes: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def search_terminology(code_type, query):
    """Search terminology codes."""
    url = f"{BASE_URL}/api/v1/terminology/{code_type}/search"
    params = {"q": query, "limit": 5}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        search_results = response.json()
        print(f"✅ Found {len(search_results['results'])} {code_type.upper()} codes for '{query}':")
        
        for result in search_results['results']:
            if code_type == 'drg':
                print(f"   • {result['drg_code']}: {result['description']}")
            else:
                print(f"   • {result['code']}: {result['description']}")
        
        return search_results
    else:
        print(f"❌ Failed to search {code_type}: {response.status_code}")
        return None

def get_reimbursement_estimate(diagnosis_codes, procedure_codes=None):
    """Get reimbursement estimate."""
    url = f"{BASE_URL}/api/v1/coding/reimbursement/estimate"
    
    request_data = {
        "diagnosis_codes": diagnosis_codes,
        "procedure_codes": procedure_codes or []
    }
    
    response = requests.post(url, json=request_data)
    
    if response.status_code == 200:
        estimate = response.json()
        print("✅ Reimbursement estimate calculated!")
        print(f"   DRG: {estimate['drg_code']}")
        print(f"   Estimated Payment: ${estimate['estimated_payment']:,.2f}")
        print(f"   Confidence: {estimate['confidence']:.1%}")
        print(f"   Explanation: {estimate['explanation']}")
        
        return estimate
    else:
        print(f"❌ Failed to get reimbursement estimate: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def get_audit_trail(claim_id):
    """Get audit trail for a claim."""
    url = f"{BASE_URL}/api/v1/audit/logs/{claim_id}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        audit_logs = response.json()
        print(f"✅ Found {len(audit_logs)} audit log entries for {claim_id}:")
        
        for log in audit_logs[:3]:  # Show first 3 entries
            timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            print(f"   • {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {log['action']}")
            print(f"     User: {log.get('user_id', 'system')}")
        
        return audit_logs
    else:
        print(f"❌ Failed to get audit trail: {response.status_code}")
        return None

def main():
    """Run the complete example workflow."""
    print("🏥 FairClaimRCM API Usage Example")
    print("=" * 50)
    
    # 1. Create a sample claim
    print("\n1. Creating sample claim...")
    claim = create_sample_claim()
    
    if not claim:
        print("Cannot continue without a valid claim. Exiting.")
        return
    
    # 2. Get coding recommendations
    print("\n2. Getting coding recommendations...")
    clinical_text = f"{claim['chief_complaint']} {claim['history_present_illness']} {claim['discharge_summary']}"
    recommendations = get_coding_recommendations(clinical_text, claim['claim_id'])
    
    # 3. Validate some codes
    print("\n3. Validating sample codes...")
    sample_codes = {
        "icd10": ["I21.9", "J44.1"],
        "cpt": ["99213", "36415"],
        "drg": ["280"]
    }
    validation = validate_codes(sample_codes)
    
    # 4. Search terminology
    print("\n4. Searching terminology...")
    search_terminology("icd10", "myocardial")
    search_terminology("cpt", "office visit")
    search_terminology("drg", "myocardial")
    
    # 5. Get reimbursement estimate
    print("\n5. Getting reimbursement estimate...")
    get_reimbursement_estimate(["I21.9"], ["99223"])
    
    # 6. Get audit trail
    print("\n6. Getting audit trail...")
    get_audit_trail(claim['claim_id'])
    
    print("\n🎉 Example completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to FairClaimRCM API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
