"""
CPT Terminology Service

Provides CPT (Current Procedural Terminology) code lookup and validation services.
"""

import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.config import settings

class CPTService:
    """
    Service for CPT procedure code management and lookup.
    
    Provides functionality to search, validate, and categorize CPT codes
    based on procedure descriptions and clinical context.
    """
    
    def __init__(self):
        self.codes_data = {}
        self.keyword_mappings = {}
        self._load_terminology_data()
    
    def _load_terminology_data(self):
        """Load CPT terminology data from JSON files."""
        try:
            data_path = Path(settings.CPT_DATA_PATH)
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.codes_data = data.get('codes', {})
                    self.keyword_mappings = data.get('keyword_mappings', {})
            else:
                # Load sample data if file doesn't exist
                self._load_sample_data()
        except Exception as e:
            print(f"Error loading CPT data: {e}")
            self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample CPT data for demonstration."""
        self.codes_data = {
            "99213": {
                "description": "Office or other outpatient visit for evaluation and management of established patient",
                "category": "Evaluation and Management",
                "base_rvu": 1.3,
                "keywords": ["office visit", "outpatient", "established patient", "evaluation", "management"]
            },
            "99223": {
                "description": "Initial hospital care, per day, comprehensive",
                "category": "Evaluation and Management",
                "base_rvu": 3.86,
                "keywords": ["hospital admission", "initial care", "comprehensive", "inpatient"]
            },
            "36415": {
                "description": "Collection of venous blood by venipuncture",
                "category": "Medicine",
                "base_rvu": 0.15,
                "keywords": ["blood draw", "venipuncture", "blood collection", "lab draw"]
            },
            "93010": {
                "description": "Electrocardiogram, routine ECG with at least 12 leads; interpretation and report only",
                "category": "Medicine",
                "base_rvu": 0.17,
                "keywords": ["ECG", "EKG", "electrocardiogram", "cardiac monitoring"]
            },
            "71020": {
                "description": "Radiologic examination, chest, 2 views, frontal and lateral",
                "category": "Radiology",
                "base_rvu": 0.32,
                "keywords": ["chest x-ray", "chest radiograph", "CXR", "chest imaging"]
            },
            "80053": {
                "description": "Comprehensive metabolic panel",
                "category": "Pathology and Laboratory",
                "base_rvu": 0.50,
                "keywords": ["CMP", "comprehensive metabolic", "blood work", "chemistry panel"]
            },
            "45378": {
                "description": "Colonoscopy, flexible; diagnostic",
                "category": "Surgery",
                "base_rvu": 4.43,
                "keywords": ["colonoscopy", "endoscopy", "colon examination", "flexible scope"]
            }
        }
        
        # Build keyword mappings
        self.keyword_mappings = {}
        for code, data in self.codes_data.items():
            for keyword in data.get('keywords', []):
                if keyword not in self.keyword_mappings:
                    self.keyword_mappings[keyword] = []
                self.keyword_mappings[keyword].append({
                    'code': code,
                    'confidence': 0.8,
                    'match_type': 'keyword'
                })
    
    async def find_codes_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Find CPT codes based on procedure keywords.
        
        Args:
            keywords: List of procedure-related keywords
            
        Returns:
            List of potential CPT codes with confidence scores
        """
        recommendations = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Direct keyword matching
            for mapped_keyword, code_matches in self.keyword_mappings.items():
                if keyword_lower in mapped_keyword.lower() or mapped_keyword.lower() in keyword_lower:
                    for match in code_matches:
                        confidence = match['confidence']
                        
                        # Boost confidence for exact matches
                        if keyword_lower == mapped_keyword.lower():
                            confidence = min(0.95, confidence + 0.1)
                        
                        recommendations.append({
                            'code': match['code'],
                            'confidence': confidence,
                            'match_reason': f"Keyword match: '{keyword}' -> '{mapped_keyword}'"
                        })
        
        # Remove duplicates and sort by confidence
        unique_recommendations = {}
        for rec in recommendations:
            code = rec['code']
            if code not in unique_recommendations or rec['confidence'] > unique_recommendations[code]['confidence']:
                unique_recommendations[code] = rec
        
        return sorted(unique_recommendations.values(), key=lambda x: x['confidence'], reverse=True)
    
    async def find_codes_by_text(self, clinical_text: str) -> List[Dict[str, Any]]:
        """
        Find CPT codes based on clinical text analysis.
        
        Args:
            clinical_text: Clinical documentation text
            
        Returns:
            List of potential CPT codes with confidence scores
        """
        recommendations = []
        text_lower = clinical_text.lower()
        
        # Pattern-based matching for common procedures
        procedure_patterns = [
            {
                'pattern': r'(office visit|outpatient visit|clinic visit)',
                'codes': ['99213'],
                'confidence': 0.8
            },
            {
                'pattern': r'(hospital admission|admitted to|inpatient)',
                'codes': ['99223'],
                'confidence': 0.8
            },
            {
                'pattern': r'(blood draw|venipuncture|blood collection)',
                'codes': ['36415'],
                'confidence': 0.9
            },
            {
                'pattern': r'(ECG|EKG|electrocardiogram)',
                'codes': ['93010'],
                'confidence': 0.9
            },
            {
                'pattern': r'(chest x-ray|chest radiograph|CXR)',
                'codes': ['71020'],
                'confidence': 0.9
            },
            {
                'pattern': r'(lab work|blood work|chemistry|metabolic panel)',
                'codes': ['80053'],
                'confidence': 0.7
            },
            {
                'pattern': r'(colonoscopy|endoscopy|scope)',
                'codes': ['45378'],
                'confidence': 0.8
            }
        ]
        
        for pattern_data in procedure_patterns:
            if re.search(pattern_data['pattern'], text_lower):
                for code in pattern_data['codes']:
                    recommendations.append({
                        'code': code,
                        'confidence': pattern_data['confidence'],
                        'match_reason': f"Pattern match: {pattern_data['pattern']}"
                    })
        
        # Remove duplicates and sort by confidence
        unique_recommendations = {}
        for rec in recommendations:
            code = rec['code']
            if code not in unique_recommendations or rec['confidence'] > unique_recommendations[code]['confidence']:
                unique_recommendations[code] = rec
        
        return sorted(unique_recommendations.values(), key=lambda x: x['confidence'], reverse=True)
    
    def get_code_description(self, code: str) -> str:
        """Get description for a CPT code."""
        return self.codes_data.get(code, {}).get('description', f"Unknown code: {code}")
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate a CPT code and return its details.
        
        Args:
            code: CPT code to validate
            
        Returns:
            Validation result with code details
        """
        if code in self.codes_data:
            return {
                'valid': True,
                'code': code,
                'description': self.codes_data[code]['description'],
                'category': self.codes_data[code]['category'],
                'base_rvu': self.codes_data[code].get('base_rvu', 0)
            }
        else:
            return {
                'valid': False,
                'code': code,
                'error': 'Code not found in terminology database'
            }
    
    def get_code_category(self, code: str) -> str:
        """Get category for a CPT code."""
        return self.codes_data.get(code, {}).get('category', 'Unknown')
    
    def get_rvu_value(self, code: str) -> float:
        """Get Relative Value Unit (RVU) for a CPT code."""
        return self.codes_data.get(code, {}).get('base_rvu', 0.0)
    
    def search_codes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search CPT codes by description or code.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching codes
        """
        results = []
        query_lower = query.lower()
        
        for code, data in self.codes_data.items():
            # Search in code
            if query_lower in code.lower():
                results.append({
                    'code': code,
                    'description': data['description'],
                    'category': data['category'],
                    'match_type': 'code',
                    'relevance': 1.0,
                    'base_rvu': data.get('base_rvu', 0)
                })
            # Search in description
            elif query_lower in data['description'].lower():
                results.append({
                    'code': code,
                    'description': data['description'],
                    'category': data['category'],
                    'match_type': 'description',
                    'relevance': 0.8,
                    'base_rvu': data.get('base_rvu', 0)
                })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]
    
    def get_codes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all CPT codes in a specific category.
        
        Args:
            category: CPT category name
            
        Returns:
            List of codes in the category
        """
        results = []
        
        for code, data in self.codes_data.items():
            if data.get('category', '').lower() == category.lower():
                results.append({
                    'code': code,
                    'description': data['description'],
                    'category': data['category'],
                    'base_rvu': data.get('base_rvu', 0)
                })
        
        return sorted(results, key=lambda x: x['code'])
