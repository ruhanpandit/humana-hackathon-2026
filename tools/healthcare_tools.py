import csv
import os

# Load data
DATA_DIR = "data/structured"

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    return []

claims_data = load_csv("claims.csv")
members_data = load_csv("members.csv")
providers_data = load_csv("providers.csv")
benefits_data = load_csv("coverage_rules.csv")
roi_data = load_csv("roi_authorizations.csv")
compliance_data = load_csv("compliance_flags.csv")

def lookup_claim(claim_id: str):
    """Analyze claim status and details."""
    for claim in claims_data:
        if claim['claim_id'] == claim_id:
            return claim
    return {"error": "Claim not found"}

def lookup_member(member_id: str):
    """Retrieve member profile and plan information."""
    for member in members_data:
        if member['member_id'] == member_id:
            return member
    return {"error": "Member not found"}

def lookup_provider(provider_id: str):
    """Get provider details and network status."""
    for provider in providers_data:
        if provider['provider_id'] == provider_id:
            return provider
    return {"error": "Provider not found"}

def lookup_benefits(member_id: str, cpt_code: str):
    """Check coverage and cost-sharing for a specific CPT code."""
    member = lookup_member(member_id)
    if "error" in member:
        return member
    
    plan_type = member['plan_type']
    for rule in benefits_data:
        if rule['plan_type'] == plan_type and rule['cpt_code'] == str(cpt_code):
            return rule
    
    return {"error": f"No coverage rule found for CPT {cpt_code} and plan {plan_type}"}

def lookup_cpt(cpt_code: str):
    """Get description and standard information for a CPT code."""
    for rule in benefits_data:
        if rule['cpt_code'] == str(cpt_code):
            return {"cpt_code": cpt_code, "description": rule['cpt_description']}
    
    for claim in claims_data:
        if claim['cpt_code'] == str(cpt_code):
            return {"cpt_code": cpt_code, "description": claim['cpt_description']}
        
    return {"error": "CPT code not found"}

def check_prior_authorization(claim_id: str):
    """Check if prior authorization was required and obtained for a claim."""
    claim = lookup_claim(claim_id)
    if "error" in claim:
        return claim
    return {
        "claim_id": claim_id,
        "required": claim['prior_auth_required'],
        "obtained": claim['prior_auth_obtained']
    }

def check_roi_status(member_id: str, caller_name: str):
    """Check if a valid Release of Information (ROI) is on file for a caller."""
    results = []
    for auth in roi_data:
        if auth['member_id'] == member_id and caller_name.lower() in auth['authorized_caller_name'].lower():
            if auth['auth_expired'] == 'True':
                return {"status": "EXPIRED", "expiration_date": auth['expiration_date']}
            return {"status": "ACTIVE", "details": auth}
    
    return {"status": "MISSING", "message": "No ROI found for this caller."}

def generate_claim_timeline(claim_id: str):
    """Build a chronological timeline of claim events."""
    claim = lookup_claim(claim_id)
    if "error" in claim:
        return claim
    
    timeline = [
        {"event": "Service Date", "date": claim['service_date']},
        {"event": "Claim Submitted", "date": claim['submitted_date']}
    ]
    
    if claim.get('adjudication_date'):
        timeline.append({"event": "Adjudication Finished", "date": claim['adjudication_date']})
        timeline.append({"event": "Status Updated", "status": claim['claim_status']})
        
    return {"claim_id": claim_id, "timeline": timeline}

def calculate_claim_risk(claim_id: str):
    """Analyze operational signals for risk and anomalies."""
    claim = lookup_claim(claim_id)
    if "error" in claim:
        return claim
    
    risk_score = 0
    factors = []
    
    if claim['denial_risk_flag'] == 'True':
        risk_score += 50
        factors.append("Systemic denial risk flag detected")
        
    if claim['modifier_mismatch'] == 'True':
        risk_score += 30
        factors.append("Modifier mismatch identified")
        
    if claim['claim_status'] == "Denied" and claim['denial_fixable'] == 'False':
        risk_score += 20
        factors.append("Non-fixable denial")
        
    provider_id = claim['provider_id']
    for flag in compliance_data:
        if flag['entity_id'] == provider_id:
            risk_score += 20
            factors.append(f"Provider has active compliance flags: {flag['flag_type']}")
            break

    return {
        "claim_id": claim_id,
        "risk_score": min(risk_score, 100),
        "risk_level": "High" if risk_score >= 70 else "Medium" if risk_score >= 30 else "Low",
        "factors": factors
    }

from tools.business_impact import calculate_business_impact

def get_business_impact_metrics():
    """Retrieve summarized business impact metrics and ROI data for AI transformation."""
    data = calculate_business_impact()
    return data['summary']
