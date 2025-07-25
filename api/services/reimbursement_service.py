"""
Enhanced Reimbursement Engine for FairClaimRCM

Comprehensive fee schedule processing, reimbursement calculations,
and payment simulation with support for multiple payers and rate schedules.
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, date
import json
import re
from decimal import Decimal, ROUND_HALF_UP

from api.services.audit_service import AuditService
from core.terminology.cpt_service import CPTService
from core.terminology.drg_service import DRGService

class ReimbursementEngine:
    """Enhanced reimbursement calculation engine with comprehensive fee schedules."""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.cpt_service = CPTService()
        self.drg_service = DRGService()
        
        # Load fee schedules
        self._load_fee_schedules()
        
    def _load_fee_schedules(self):
        """Load various fee schedules and rate tables."""
        # Mock Medicare fee schedule (2024)
        self.medicare_fee_schedule = {
            # Evaluation & Management
            "99201": {"work_rvu": 0.00, "pe_rvu": 0.00, "mp_rvu": 0.00, "conversion_factor": 33.2875},  # Discontinued
            "99202": {"work_rvu": 0.93, "pe_rvu": 1.21, "mp_rvu": 0.07, "conversion_factor": 33.2875},
            "99203": {"work_rvu": 1.60, "pe_rvu": 1.92, "mp_rvu": 0.12, "conversion_factor": 33.2875},
            "99204": {"work_rvu": 2.60, "pe_rvu": 2.56, "mp_rvu": 0.19, "conversion_factor": 33.2875},
            "99205": {"work_rvu": 3.50, "pe_rvu": 3.04, "mp_rvu": 0.24, "conversion_factor": 33.2875},
            "99211": {"work_rvu": 0.00, "pe_rvu": 0.61, "mp_rvu": 0.02, "conversion_factor": 33.2875},
            "99212": {"work_rvu": 0.48, "pe_rvu": 0.85, "mp_rvu": 0.04, "conversion_factor": 33.2875},
            "99213": {"work_rvu": 0.97, "pe_rvu": 1.18, "mp_rvu": 0.07, "conversion_factor": 33.2875},
            "99214": {"work_rvu": 1.50, "pe_rvu": 1.66, "mp_rvu": 0.10, "conversion_factor": 33.2875},
            "99215": {"work_rvu": 2.11, "pe_rvu": 2.16, "mp_rvu": 0.14, "conversion_factor": 33.2875},
            
            # Procedures
            "36415": {"work_rvu": 0.17, "pe_rvu": 0.24, "mp_rvu": 0.01, "conversion_factor": 33.2875},  # Venipuncture
            "81003": {"work_rvu": 0.00, "pe_rvu": 0.14, "mp_rvu": 0.00, "conversion_factor": 33.2875},  # Urinalysis
            "85025": {"work_rvu": 0.00, "pe_rvu": 0.28, "mp_rvu": 0.00, "conversion_factor": 33.2875},  # CBC
            "80053": {"work_rvu": 0.00, "pe_rvu": 0.35, "mp_rvu": 0.00, "conversion_factor": 33.2875},  # Comprehensive metabolic panel
        }
        
        # Commercial insurance multipliers
        self.commercial_multipliers = {
            "aetna": 1.15,
            "anthem": 1.20,
            "cigna": 1.18,
            "united_healthcare": 1.22,
            "humana": 1.12,
            "default": 1.20
        }
        
        # State Medicaid rates (percentage of Medicare)
        self.medicaid_rates = {
            "AL": 0.75, "AK": 1.20, "AZ": 0.85, "AR": 0.70, "CA": 0.95,
            "CO": 0.90, "CT": 1.05, "DE": 0.85, "FL": 0.80, "GA": 0.75,
            "default": 0.80
        }
        
        # DRG base rates
        self.drg_base_rates = {
            "001": 15000, "002": 12000, "003": 10000, "470": 45000,
            "default": 8000
        }

    async def calculate_claim_reimbursement(
        self, 
        claim_id: str,
        cpt_codes: List[str],
        icd10_codes: List[str],
        drg_code: Optional[str] = None,
        payer_type: str = "medicare",
        payer_name: Optional[str] = None,
        state: str = "default",
        service_date: Optional[date] = None,
        modifiers: Optional[List[str]] = None,
        units: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive reimbursement for a claim.
        
        Args:
            claim_id: Unique claim identifier
            cpt_codes: List of CPT procedure codes
            icd10_codes: List of ICD-10 diagnosis codes
            drg_code: DRG code (if applicable)
            payer_type: Type of payer (medicare, medicaid, commercial)
            payer_name: Specific payer name
            state: State for Medicaid calculations
            service_date: Date of service
            modifiers: CPT modifiers
            units: Units for each CPT code
            
        Returns:
            Dict containing detailed reimbursement calculation
        """
        try:
            calculation_start = datetime.utcnow()
            service_date = service_date or date.today()
            modifiers = modifiers or []
            units = units or {}
            
            # Initialize calculation results
            calculation = {
                "claim_id": claim_id,
                "calculation_date": calculation_start.isoformat(),
                "service_date": service_date.isoformat(),
                "payer_type": payer_type,
                "payer_name": payer_name,
                "state": state,
                "cpt_calculations": [],
                "drg_calculation": None,
                "total_charges": Decimal("0.00"),
                "total_allowed": Decimal("0.00"),
                "total_reimbursement": Decimal("0.00"),
                "adjustments": [],
                "denials": [],
                "warnings": []
            }
            
            # Calculate CPT-based reimbursement
            if cpt_codes:
                cpt_total = await self._calculate_cpt_reimbursement(
                    cpt_codes, payer_type, payer_name, state, modifiers, units
                )
                calculation["cpt_calculations"] = cpt_total["line_items"]
                calculation["total_charges"] += cpt_total["total_charges"]
                calculation["total_allowed"] += cpt_total["total_allowed"]
                calculation["total_reimbursement"] += cpt_total["total_reimbursement"]
                calculation["adjustments"].extend(cpt_total["adjustments"])
                calculation["warnings"].extend(cpt_total["warnings"])
            
            # Calculate DRG-based reimbursement (for inpatient)
            if drg_code:
                drg_calculation = await self._calculate_drg_reimbursement(
                    drg_code, payer_type, payer_name, state
                )
                calculation["drg_calculation"] = drg_calculation
                calculation["total_reimbursement"] = drg_calculation["payment_amount"]
            
            # Apply global adjustments
            calculation = await self._apply_global_adjustments(calculation, icd10_codes)
            
            # Validate against coverage rules
            validation_result = await self._validate_coverage(
                cpt_codes, icd10_codes, payer_type, payer_name
            )
            calculation["coverage_validation"] = validation_result
            
            # Calculate patient responsibility
            calculation["patient_responsibility"] = await self._calculate_patient_responsibility(
                calculation, payer_type
            )
            
            # Add summary
            calculation["summary"] = {
                "total_charges": float(calculation["total_charges"]),
                "total_allowed": float(calculation["total_allowed"]),
                "total_reimbursement": float(calculation["total_reimbursement"]),
                "patient_responsibility": calculation["patient_responsibility"],
                "adjustment_count": len(calculation["adjustments"]),
                "warning_count": len(calculation["warnings"]),
                "calculation_time_ms": (datetime.utcnow() - calculation_start).total_seconds() * 1000
            }
            
            # Log calculation
            await self.audit_service.log_activity(
                claim_id=claim_id,
                action="reimbursement_calculated",
                details={
                    "payer_type": payer_type,
                    "total_reimbursement": float(calculation["total_reimbursement"]),
                    "cpt_count": len(cpt_codes),
                    "drg_code": drg_code
                }
            )
            
            return calculation
            
        except Exception as e:
            raise Exception(f"Failed to calculate reimbursement: {str(e)}")

    async def _calculate_cpt_reimbursement(
        self,
        cpt_codes: List[str],
        payer_type: str,
        payer_name: Optional[str],
        state: str,
        modifiers: List[str],
        units: Dict[str, int]
    ) -> Dict[str, Any]:
        """Calculate fee-for-service reimbursement for CPT codes."""
        line_items = []
        total_charges = Decimal("0.00")
        total_allowed = Decimal("0.00")
        total_reimbursement = Decimal("0.00")
        adjustments = []
        warnings = []
        
        for cpt_code in cpt_codes:
            try:
                # Get CPT details
                cpt_details = self.cpt_service.get_code_details(cpt_code)
                if not cpt_details:
                    warnings.append(f"CPT code {cpt_code} not found")
                    continue
                
                # Get fee schedule data
                fee_data = self.medicare_fee_schedule.get(cpt_code)
                if not fee_data:
                    # Use default rates for unknown codes
                    fee_data = {
                        "work_rvu": 1.0,
                        "pe_rvu": 1.0,
                        "mp_rvu": 0.05,
                        "conversion_factor": 33.2875
                    }
                    warnings.append(f"Using default rates for CPT {cpt_code}")
                
                # Calculate base Medicare amount
                total_rvu = fee_data["work_rvu"] + fee_data["pe_rvu"] + fee_data["mp_rvu"]
                medicare_amount = Decimal(str(total_rvu * fee_data["conversion_factor"]))
                
                # Apply units
                code_units = units.get(cpt_code, 1)
                charges = medicare_amount * code_units
                
                # Apply payer-specific adjustments
                if payer_type == "medicare":
                    allowed_amount = charges
                    reimbursement = charges * Decimal("0.80")  # 80% Medicare coinsurance
                elif payer_type == "medicaid":
                    medicaid_rate = self.medicaid_rates.get(state, self.medicaid_rates["default"])
                    allowed_amount = charges * Decimal(str(medicaid_rate))
                    reimbursement = allowed_amount
                else:  # Commercial
                    multiplier = self.commercial_multipliers.get(
                        payer_name.lower() if payer_name else "default",
                        self.commercial_multipliers["default"]
                    )
                    allowed_amount = charges * Decimal(str(multiplier))
                    reimbursement = allowed_amount * Decimal("0.90")  # 90% commercial coinsurance
                
                # Apply modifiers
                modifier_adjustment = self._apply_cpt_modifiers(modifiers, reimbursement)
                final_reimbursement = reimbursement + modifier_adjustment
                
                line_item = {
                    "cpt_code": cpt_code,
                    "description": cpt_details.get("description", ""),
                    "units": code_units,
                    "charges": float(charges),
                    "allowed_amount": float(allowed_amount),
                    "reimbursement": float(final_reimbursement),
                    "rvu_details": {
                        "work_rvu": fee_data["work_rvu"],
                        "pe_rvu": fee_data["pe_rvu"],
                        "mp_rvu": fee_data["mp_rvu"],
                        "total_rvu": total_rvu,
                        "conversion_factor": fee_data["conversion_factor"]
                    },
                    "modifiers": modifiers
                }
                
                if modifier_adjustment != 0:
                    adjustments.append({
                        "cpt_code": cpt_code,
                        "type": "modifier_adjustment",
                        "amount": float(modifier_adjustment),
                        "description": f"Modifier adjustment for {', '.join(modifiers)}"
                    })
                
                line_items.append(line_item)
                total_charges += charges
                total_allowed += allowed_amount
                total_reimbursement += final_reimbursement
                
            except Exception as e:
                warnings.append(f"Error calculating CPT {cpt_code}: {str(e)}")
        
        return {
            "line_items": line_items,
            "total_charges": total_charges,
            "total_allowed": total_allowed,
            "total_reimbursement": total_reimbursement,
            "adjustments": adjustments,
            "warnings": warnings
        }

    async def _calculate_drg_reimbursement(
        self,
        drg_code: str,
        payer_type: str,
        payer_name: Optional[str],
        state: str
    ) -> Dict[str, Any]:
        """Calculate DRG-based reimbursement for inpatient stays."""
        try:
            # Get DRG details
            drg_details = self.drg_service.get_drg_details(drg_code)
            if not drg_details:
                raise ValueError(f"DRG code {drg_code} not found")
            
            # Get base payment rate
            base_rate = self.drg_base_rates.get(drg_code, self.drg_base_rates["default"])
            
            # Apply payer-specific adjustments
            if payer_type == "medicare":
                payment_amount = Decimal(str(base_rate))
            elif payer_type == "medicaid":
                medicaid_rate = self.medicaid_rates.get(state, self.medicaid_rates["default"])
                payment_amount = Decimal(str(base_rate * medicaid_rate))
            else:  # Commercial
                multiplier = self.commercial_multipliers.get(
                    payer_name.lower() if payer_name else "default",
                    self.commercial_multipliers["default"]
                )
                payment_amount = Decimal(str(base_rate * multiplier))
            
            return {
                "drg_code": drg_code,
                "description": drg_details.get("description", ""),
                "base_rate": base_rate,
                "payment_amount": payment_amount,
                "weight": drg_details.get("weight", 1.0),
                "los_geometric_mean": drg_details.get("los_geometric_mean", 0),
                "los_arithmetic_mean": drg_details.get("los_arithmetic_mean", 0)
            }
            
        except Exception as e:
            raise Exception(f"Failed to calculate DRG reimbursement: {str(e)}")

    def _apply_cpt_modifiers(self, modifiers: List[str], base_amount: Decimal) -> Decimal:
        """Apply CPT modifier adjustments."""
        adjustment = Decimal("0.00")
        
        for modifier in modifiers:
            if modifier == "50":  # Bilateral procedure
                adjustment += base_amount * Decimal("0.50")
            elif modifier == "51":  # Multiple procedures
                adjustment -= base_amount * Decimal("0.25")
            elif modifier == "52":  # Reduced services
                adjustment -= base_amount * Decimal("0.50")
            elif modifier == "22":  # Increased procedural services
                adjustment += base_amount * Decimal("0.25")
            elif modifier == "53":  # Discontinued procedure
                adjustment -= base_amount * Decimal("0.75")
        
        return adjustment

    async def _apply_global_adjustments(
        self,
        calculation: Dict[str, Any],
        icd10_codes: List[str]
    ) -> Dict[str, Any]:
        """Apply global adjustments based on diagnosis codes and other factors."""
        adjustments = calculation.get("adjustments", [])
        
        # Check for high-cost diagnoses
        high_cost_diagnoses = ["C78", "C79", "I21", "I22"]  # Cancer metastases, MI
        for icd_code in icd10_codes:
            for high_cost in high_cost_diagnoses:
                if icd_code.startswith(high_cost):
                    adjustment_amount = calculation["total_reimbursement"] * Decimal("0.10")
                    calculation["total_reimbursement"] += adjustment_amount
                    adjustments.append({
                        "type": "high_cost_diagnosis",
                        "amount": float(adjustment_amount),
                        "description": f"High-cost diagnosis adjustment for {icd_code}"
                    })
                    break
        
        calculation["adjustments"] = adjustments
        return calculation

    async def _validate_coverage(
        self,
        cpt_codes: List[str],
        icd10_codes: List[str],
        payer_type: str,
        payer_name: Optional[str]
    ) -> Dict[str, Any]:
        """Validate coverage rules and medical necessity."""
        validation = {
            "is_covered": True,
            "coverage_issues": [],
            "prior_auth_required": [],
            "medical_necessity_met": True
        }
        
        # Check for codes requiring prior authorization
        prior_auth_codes = ["99091", "99453", "99454"]  # Telehealth and remote monitoring
        for cpt_code in cpt_codes:
            if cpt_code in prior_auth_codes:
                validation["prior_auth_required"].append({
                    "cpt_code": cpt_code,
                    "reason": "Requires prior authorization"
                })
        
        # Check medical necessity (simplified)
        for cpt_code in cpt_codes:
            if cpt_code.startswith("99") and not icd10_codes:  # E&M without diagnosis
                validation["medical_necessity_met"] = False
                validation["coverage_issues"].append({
                    "cpt_code": cpt_code,
                    "issue": "Missing supporting diagnosis codes"
                })
        
        return validation

    async def _calculate_patient_responsibility(
        self,
        calculation: Dict[str, Any],
        payer_type: str
    ) -> Dict[str, Any]:
        """Calculate patient financial responsibility."""
        total_reimbursement = calculation["total_reimbursement"]
        total_charges = calculation["total_charges"]
        
        if payer_type == "medicare":
            # Medicare Part B: 20% coinsurance after deductible
            deductible = Decimal("240.00")  # 2024 Medicare Part B deductible
            coinsurance_rate = Decimal("0.20")
            patient_coinsurance = total_reimbursement * coinsurance_rate
            patient_responsibility = deductible + patient_coinsurance
        elif payer_type == "medicaid":
            # Medicaid typically has minimal patient responsibility
            patient_responsibility = Decimal("5.00")  # Nominal copay
        else:  # Commercial
            # Typical commercial plan: $500 deductible, 20% coinsurance
            deductible = Decimal("500.00")
            coinsurance_rate = Decimal("0.20")
            patient_coinsurance = (total_charges - deductible) * coinsurance_rate
            patient_responsibility = max(deductible, patient_coinsurance)
        
        return {
            "total_amount": float(patient_responsibility),
            "deductible": float(deductible if payer_type != "medicaid" else Decimal("0.00")),
            "coinsurance": float(patient_coinsurance if payer_type != "medicaid" else Decimal("0.00")),
            "copay": float(Decimal("5.00") if payer_type == "medicaid" else Decimal("0.00"))
        }

    async def get_fee_schedule_info(
        self,
        cpt_code: str,
        payer_type: str = "medicare"
    ) -> Dict[str, Any]:
        """Get detailed fee schedule information for a specific CPT code."""
        if payer_type == "medicare" and cpt_code in self.medicare_fee_schedule:
            fee_data = self.medicare_fee_schedule[cpt_code]
            total_rvu = fee_data["work_rvu"] + fee_data["pe_rvu"] + fee_data["mp_rvu"]
            payment_amount = total_rvu * fee_data["conversion_factor"]
            
            return {
                "cpt_code": cpt_code,
                "payer_type": payer_type,
                "rvu_components": {
                    "work_rvu": fee_data["work_rvu"],
                    "practice_expense_rvu": fee_data["pe_rvu"],
                    "malpractice_rvu": fee_data["mp_rvu"],
                    "total_rvu": total_rvu
                },
                "conversion_factor": fee_data["conversion_factor"],
                "payment_amount": round(payment_amount, 2),
                "year": 2024
            }
        
        return {"error": f"Fee schedule data not available for {cpt_code} under {payer_type}"}

    async def simulate_payment_scenarios(
        self,
        cpt_codes: List[str],
        icd10_codes: List[str],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate reimbursement across multiple payer scenarios."""
        results = []
        
        for scenario in scenarios:
            try:
                calculation = await self.calculate_claim_reimbursement(
                    claim_id=f"simulation_{scenario.get('name', 'unknown')}",
                    cpt_codes=cpt_codes,
                    icd10_codes=icd10_codes,
                    payer_type=scenario.get("payer_type", "medicare"),
                    payer_name=scenario.get("payer_name"),
                    state=scenario.get("state", "default")
                )
                
                results.append({
                    "scenario_name": scenario.get("name", "Unnamed"),
                    "payer_type": scenario.get("payer_type"),
                    "payer_name": scenario.get("payer_name"),
                    "total_reimbursement": calculation["summary"]["total_reimbursement"],
                    "patient_responsibility": calculation["patient_responsibility"]["total_amount"],
                    "coverage_issues": len(calculation["coverage_validation"]["coverage_issues"])
                })
                
            except Exception as e:
                results.append({
                    "scenario_name": scenario.get("name", "Unnamed"),
                    "error": str(e)
                })
        
        # Add comparison summary
        valid_results = [r for r in results if "error" not in r]
        if valid_results:
            reimbursements = [r["total_reimbursement"] for r in valid_results]
            comparison = {
                "highest_reimbursement": max(reimbursements),
                "lowest_reimbursement": min(reimbursements),
                "average_reimbursement": sum(reimbursements) / len(reimbursements),
                "variance": max(reimbursements) - min(reimbursements)
            }
        else:
            comparison = {"error": "No valid scenarios"}
        
        return {
            "scenarios": results,
            "comparison": comparison,
            "simulation_date": datetime.utcnow().isoformat()
        }
