"""
ICD-10 Terminology Service

Provides ICD-10 code lookup, validation, and classification services.
"""

import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.config import settings

class ICD10Service:
    """
    Service for ICD-10 diagnosis code management and lookup.
    
    Provides functionality to search, validate, and categorize ICD-10 codes
    based on clinical text and symptoms.
    """
    
    def __init__(self):
        self.codes_data = {}
        self.keyword_mappings = {}
        self._load_terminology_data()
    
    def _load_terminology_data(self):
        """Load ICD-10 terminology data from JSON files."""
        try:
            data_path = Path(settings.ICD10_DATA_PATH)
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.codes_data = data.get('codes', {})
                    self.keyword_mappings = data.get('keyword_mappings', {})
            else:
                # Load sample data if file doesn't exist
                self._load_sample_data()
        except Exception as e:
            print(f"Error loading ICD-10 data: {e}")
            self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample ICD-10 data for demonstration."""
        self.codes_data = {
            "I21.9": {
                "description": "Acute myocardial infarction, unspecified",
                "category": "Diseases of the circulatory system",
                "billable": True,
                "keywords": ["myocardial infarction", "heart attack", "MI", "chest pain", "cardiac arrest"]
            },
            "J44.1": {
                "description": "Chronic obstructive pulmonary disease with acute exacerbation",
                "category": "Diseases of the respiratory system",
                "billable": True,
                "keywords": ["COPD", "chronic obstructive", "breathing difficulty", "shortness of breath"]
            },
            "N18.6": {
                "description": "End stage renal disease",
                "category": "Diseases of the genitourinary system",
                "billable": True,
                "keywords": ["kidney failure", "renal failure", "dialysis", "ESRD"]
            },
            "E11.9": {
                "description": "Type 2 diabetes mellitus without complications",
                "category": "Endocrine, nutritional and metabolic diseases",
                "billable": True,
                "keywords": ["diabetes", "blood sugar", "hyperglycemia", "diabetic"]
            },
            "K92.2": {
                "description": "Gastrointestinal hemorrhage, unspecified",
                "category": "Diseases of the digestive system",
                "billable": True,
                "keywords": ["GI bleed", "gastrointestinal bleeding", "blood in stool", "hematemesis"]
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
    
    async def find_codes_by_text(self, clinical_text: str) -> List[Dict[str, Any]]:
        """
        Find ICD-10 codes based on clinical text analysis.
        
        Args:
            clinical_text: Clinical documentation text
            
        Returns:
            List of potential ICD-10 codes with confidence scores
        """
        recommendations = []
        text_lower = clinical_text.lower()
        
        # Direct keyword matching
        for keyword, code_matches in self.keyword_mappings.items():
            if keyword.lower() in text_lower:
                for match in code_matches:
                    # Calculate confidence based on keyword prominence
                    keyword_count = text_lower.count(keyword.lower())
                    confidence = min(0.95, match['confidence'] + (keyword_count - 1) * 0.1)
                    
                    recommendations.append({
                        'code': match['code'],
                        'confidence': confidence,
                        'match_reason': f"Keyword match: '{keyword}'"
                    })
        
        # Pattern-based matching for common medical phrases
        pattern_matches = self._pattern_based_matching(clinical_text)
        recommendations.extend(pattern_matches)
        
        # Remove duplicates and sort by confidence
        unique_recommendations = {}
        for rec in recommendations:
            code = rec['code']
            if code not in unique_recommendations or rec['confidence'] > unique_recommendations[code]['confidence']:
                unique_recommendations[code] = rec
        
        return sorted(unique_recommendations.values(), key=lambda x: x['confidence'], reverse=True)
    
    def _pattern_based_matching(self, text: str) -> List[Dict[str, Any]]:
        """Apply pattern-based matching for ICD-10 codes."""
        patterns = [
            # Cardiovascular patterns
            {
                'pattern': r'(chest pain|cardiac|myocardial|heart attack)',
                'codes': ['I21.9'],
                'confidence': 0.7
            },
            # Respiratory patterns
            {
                'pattern': r'(shortness of breath|dyspnea|COPD|respiratory)',
                'codes': ['J44.1'],
                'confidence': 0.7
            },
            # Diabetes patterns
            {
                'pattern': r'(diabetes|diabetic|blood sugar|hyperglycemia)',
                'codes': ['E11.9'],
                'confidence': 0.75
            },
            # Renal patterns
            {
                'pattern': r'(kidney|renal|dialysis|nephritis)',
                'codes': ['N18.6'],
                'confidence': 0.7
            }
        ]
        
        recommendations = []
        for pattern_data in patterns:
            if re.search(pattern_data['pattern'], text, re.IGNORECASE):
                for code in pattern_data['codes']:
                    recommendations.append({
                        'code': code,
                        'confidence': pattern_data['confidence'],
                        'match_reason': f"Pattern match: {pattern_data['pattern']}"
                    })
        
        return recommendations
    
    def get_code_description(self, code: str) -> str:
        """Get description for an ICD-10 code."""
        return self.codes_data.get(code, {}).get('description', f"Unknown code: {code}")
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate an ICD-10 code and return its details.
        
        Args:
            code: ICD-10 code to validate
            
        Returns:
            Validation result with code details
        """
        if code in self.codes_data:
            return {
                'valid': True,
                'code': code,
                'description': self.codes_data[code]['description'],
                'category': self.codes_data[code]['category'],
                'billable': self.codes_data[code]['billable']
            }
        else:
            return {
                'valid': False,
                'code': code,
                'error': 'Code not found in terminology database'
            }
    
    def get_code_hierarchy(self, code: str) -> List[str]:
        """
        Get the hierarchical path for an ICD-10 code.
        
        Args:
            code: ICD-10 code
            
        Returns:
            List of parent codes in hierarchy
        """
        # Simplified hierarchy based on ICD-10 structure
        hierarchy = []
        
        if len(code) >= 1:
            hierarchy.append(code[0])  # Chapter
        if len(code) >= 3:
            hierarchy.append(code[:3])  # Category
        if len(code) >= 4:
            hierarchy.append(code[:4])  # Subcategory
        
        return hierarchy
    
    def search_codes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search ICD-10 codes by description or code.
        
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
                    'relevance': 1.0
                })
            # Search in description
            elif query_lower in data['description'].lower():
                results.append({
                    'code': code,
                    'description': data['description'],
                    'category': data['category'],
                    'match_type': 'description',
                    'relevance': 0.8
                })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]
