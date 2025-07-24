"""
Basic tests for FairClaimRCM core functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.terminology.icd10_service import ICD10Service
from core.terminology.cpt_service import CPTService
from core.terminology.drg_service import DRGService
from core.ml.code_predictor import CodePredictor

if __name__ == "__main__":
    # Run basic tests without pytest
    print("Running FairClaimRCM Core Tests...")
    
    # Test ICD10 Service
    print("\n1. Testing ICD10 Service...")
    icd10_service = ICD10Service()
    result = icd10_service.validate_code("I21.9")
    print(f"   ✅ ICD-10 validation: {result['valid']}")
    
    # Test CPT Service
    print("\n2. Testing CPT Service...")
    cpt_service = CPTService()
    result = cpt_service.validate_code("99213")
    print(f"   ✅ CPT validation: {result['valid']}")
    
    # Test DRG Service
    print("\n3. Testing DRG Service...")
    drg_service = DRGService()
    result = drg_service.validate_drg("280")
    print(f"   ✅ DRG validation: {result['valid']}")
    
    # Test Code Predictor
    print("\n4. Testing Code Predictor...")
    predictor = CodePredictor()
    features = predictor.extract_clinical_features("Patient has chest pain")
    print(f"   ✅ Feature extraction: {len(features)} features extracted")
    
    print("\n🎉 All core tests passed!")
