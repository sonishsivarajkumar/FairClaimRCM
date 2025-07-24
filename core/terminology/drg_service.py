"""
DRG (Diagnosis Related Group) Service

Provides DRG classification and reimbursement calculation services.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.config import settings

class DRGService:
    """
    Service for DRG classification and reimbursement calculation.
    
    Determines appropriate DRG assignments based on primary and secondary
    diagnoses, procedures, and patient characteristics.
    """
    
    def __init__(self):
        self.drg_data = {}
        self.diagnosis_mappings = {}
        self._load_terminology_data()
    
    def _load_terminology_data(self):
        """Load DRG terminology data from JSON files."""
        try:
            data_path = Path(settings.DRG_DATA_PATH)
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.drg_data = data.get('drgs', {})
                    self.diagnosis_mappings = data.get('diagnosis_mappings', {})
            else:
                # Load sample data if file doesn't exist
                self._load_sample_data()
        except Exception as e:
            print(f"Error loading DRG data: {e}")
            self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample DRG data for demonstration."""
        self.drg_data = {
            "280": {
                "description": "Acute Myocardial Infarction, Discharged Alive with MCC",
                "mdc": "05",
                "mdc_description": "Diseases and Disorders of the Circulatory System",
                "type": "MEDICAL",
                "geometric_mean_los": 4.8,
                "base_weight": 2.3456,
                "relative_weight": 2.3456,
                "primary_diagnoses": ["I21.0", "I21.1", "I21.2", "I21.9"]
            },
            "281": {
                "description": "Acute Myocardial Infarction, Discharged Alive with CC",
                "mdc": "05",
                "mdc_description": "Diseases and Disorders of the Circulatory System",
                "type": "MEDICAL",
                "geometric_mean_los": 3.2,
                "base_weight": 1.4567,
                "relative_weight": 1.4567,
                "primary_diagnoses": ["I21.0", "I21.1", "I21.2", "I21.9"]
            },
            "282": {
                "description": "Acute Myocardial Infarction, Discharged Alive without CC/MCC",
                "mdc": "05",
                "mdc_description": "Diseases and Disorders of the Circulatory System",
                "type": "MEDICAL",
                "geometric_mean_los": 2.1,
                "base_weight": 0.9234,
                "relative_weight": 0.9234,
                "primary_diagnoses": ["I21.0", "I21.1", "I21.2", "I21.9"]
            },
            "190": {
                "description": "Chronic Obstructive Pulmonary Disease with MCC",
                "mdc": "04",
                "mdc_description": "Diseases and Disorders of the Respiratory System",
                "type": "MEDICAL",
                "geometric_mean_los": 4.5,
                "base_weight": 1.8901,
                "relative_weight": 1.8901,
                "primary_diagnoses": ["J44.0", "J44.1", "J44.9"]
            },
            "191": {
                "description": "Chronic Obstructive Pulmonary Disease with CC",
                "mdc": "04",
                "mdc_description": "Diseases and Disorders of the Respiratory System",
                "type": "MEDICAL",
                "geometric_mean_los": 3.1,
                "base_weight": 1.2345,
                "relative_weight": 1.2345,
                "primary_diagnoses": ["J44.0", "J44.1", "J44.9"]
            },
            "638": {
                "description": "Diabetes with CC",
                "mdc": "10",
                "mdc_description": "Endocrine, Nutritional and Metabolic Diseases and Disorders",
                "type": "MEDICAL",
                "geometric_mean_los": 3.8,
                "base_weight": 1.1567,
                "relative_weight": 1.1567,
                "primary_diagnoses": ["E11.0", "E11.1", "E11.9"]
            },
            "684": {
                "description": "Renal Failure with MCC",
                "mdc": "11",
                "mdc_description": "Diseases and Disorders of the Kidney and Urinary Tract",
                "type": "MEDICAL",
                "geometric_mean_los": 5.2,
                "base_weight": 2.1234,
                "relative_weight": 2.1234,
                "primary_diagnoses": ["N18.5", "N18.6", "N19"]
            }
        }
        
        # Build diagnosis to DRG mappings
        self.diagnosis_mappings = {}
        for drg_code, drg_data in self.drg_data.items():
            for diagnosis in drg_data.get('primary_diagnoses', []):
                if diagnosis not in self.diagnosis_mappings:
                    self.diagnosis_mappings[diagnosis] = []
                self.diagnosis_mappings[diagnosis].append(drg_code)
    
    async def find_drg_by_diagnosis(
        self, 
        primary_diagnosis: str, 
        secondary_diagnoses: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find appropriate DRG based on primary and secondary diagnoses.
        
        Args:
            primary_diagnosis: Primary ICD-10 diagnosis code
            secondary_diagnoses: List of secondary ICD-10 diagnosis codes
            
        Returns:
            DRG assignment with confidence score
        """
        secondary_diagnoses = secondary_diagnoses or []
        
        # Find potential DRGs for primary diagnosis
        potential_drgs = self.diagnosis_mappings.get(primary_diagnosis, [])
        
        if not potential_drgs:
            # Try to find by code prefix (e.g., I21.9 -> I21)
            prefix = primary_diagnosis[:3]
            for diag_code, drg_list in self.diagnosis_mappings.items():
                if diag_code.startswith(prefix):
                    potential_drgs.extend(drg_list)
        
        if not potential_drgs:
            return None
        
        # Determine complexity level based on secondary diagnoses
        complexity_level = self._determine_complexity_level(secondary_diagnoses)
        
        # Select most appropriate DRG based on complexity
        selected_drg = self._select_drg_by_complexity(potential_drgs, complexity_level)
        
        if selected_drg:
            confidence = 0.8
            if complexity_level == "MCC":
                confidence = 0.9
            elif complexity_level == "CC":
                confidence = 0.85
            
            return {
                'code': selected_drg,
                'confidence': confidence,
                'complexity_level': complexity_level,
                'description': self.drg_data[selected_drg]['description'],
                'relative_weight': self.drg_data[selected_drg]['relative_weight']
            }
        
        return None
    
    def _determine_complexity_level(self, secondary_diagnoses: List[str]) -> str:
        """
        Determine complexity level (MCC/CC/None) based on secondary diagnoses.
        
        Args:
            secondary_diagnoses: List of secondary diagnosis codes
            
        Returns:
            Complexity level: "MCC", "CC", or "None"
        """
        # Simplified complexity determination
        # In practice, this would use official CC/MCC lists
        
        mcc_indicators = ["N18.6", "I21", "J44.0"]  # Major complications
        cc_indicators = ["E11", "I10", "J44.1"]     # Complications
        
        for diagnosis in secondary_diagnoses:
            # Check for MCC
            for mcc in mcc_indicators:
                if diagnosis.startswith(mcc):
                    return "MCC"
            
            # Check for CC
            for cc in cc_indicators:
                if diagnosis.startswith(cc):
                    return "CC"
        
        return "None"
    
    def _select_drg_by_complexity(self, drg_codes: List[str], complexity_level: str) -> Optional[str]:
        """
        Select the most appropriate DRG based on complexity level.
        
        Args:
            drg_codes: List of potential DRG codes
            complexity_level: Patient complexity level
            
        Returns:
            Selected DRG code
        """
        # Sort DRGs by relative weight (higher weight typically = higher complexity)
        sorted_drgs = sorted(
            drg_codes, 
            key=lambda x: self.drg_data.get(x, {}).get('relative_weight', 0),
            reverse=True
        )
        
        if complexity_level == "MCC":
            # Select highest weight DRG
            return sorted_drgs[0] if sorted_drgs else None
        elif complexity_level == "CC":
            # Select middle weight DRG if available
            if len(sorted_drgs) >= 2:
                return sorted_drgs[1]
            elif sorted_drgs:
                return sorted_drgs[0]
        else:
            # Select lowest weight DRG
            return sorted_drgs[-1] if sorted_drgs else None
        
        return None
    
    def get_drg_description(self, drg_code: str) -> str:
        """Get description for a DRG code."""
        return self.drg_data.get(drg_code, {}).get('description', f"Unknown DRG: {drg_code}")
    
    def calculate_reimbursement(
        self, 
        drg_code: str, 
        base_rate: float = 5000.0,
        wage_index: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate estimated reimbursement for a DRG.
        
        Args:
            drg_code: DRG code
            base_rate: Hospital base rate
            wage_index: Geographic wage index
            
        Returns:
            Reimbursement calculation details
        """
        if drg_code not in self.drg_data:
            return {
                'error': f'DRG {drg_code} not found',
                'estimated_payment': 0
            }
        
        drg_info = self.drg_data[drg_code]
        relative_weight = drg_info['relative_weight']
        
        # Simplified reimbursement calculation
        estimated_payment = base_rate * relative_weight * wage_index
        
        return {
            'drg_code': drg_code,
            'description': drg_info['description'],
            'relative_weight': relative_weight,
            'base_rate': base_rate,
            'wage_index': wage_index,
            'estimated_payment': round(estimated_payment, 2),
            'geometric_mean_los': drg_info.get('geometric_mean_los', 0)
        }
    
    def validate_drg(self, drg_code: str) -> Dict[str, Any]:
        """
        Validate a DRG code and return its details.
        
        Args:
            drg_code: DRG code to validate
            
        Returns:
            Validation result with DRG details
        """
        if drg_code in self.drg_data:
            return {
                'valid': True,
                'drg_code': drg_code,
                'description': self.drg_data[drg_code]['description'],
                'mdc': self.drg_data[drg_code]['mdc'],
                'type': self.drg_data[drg_code]['type'],
                'relative_weight': self.drg_data[drg_code]['relative_weight']
            }
        else:
            return {
                'valid': False,
                'drg_code': drg_code,
                'error': 'DRG not found in database'
            }
    
    def search_drgs(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search DRGs by description or code.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching DRGs
        """
        results = []
        query_lower = query.lower()
        
        for drg_code, data in self.drg_data.items():
            # Search in code
            if query_lower in drg_code.lower():
                results.append({
                    'drg_code': drg_code,
                    'description': data['description'],
                    'mdc': data['mdc'],
                    'relative_weight': data['relative_weight'],
                    'match_type': 'code',
                    'relevance': 1.0
                })
            # Search in description
            elif query_lower in data['description'].lower():
                results.append({
                    'drg_code': drg_code,
                    'description': data['description'],
                    'mdc': data['mdc'],
                    'relative_weight': data['relative_weight'],
                    'match_type': 'description',
                    'relevance': 0.8
                })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]
