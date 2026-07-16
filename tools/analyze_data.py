import csv
import json
import os

DATA_DIR = "humana-hackathon-2026/data/structured"

def analyze_synthetic_data():
    stats = {
        "claims": {"total": 0, "denied": 0, "fixable_denials": 0, "modifiers": 0, "risk_flags": 0},
        "roi": {"total": 0, "expired": 0},
        "compliance": {"denial_rates": []}
    }

    # Claims Analysis
    claims_path = os.path.join(DATA_DIR, "claims.csv")
    if os.path.exists(claims_path):
        with open(claims_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats["claims"]["total"] += 1
                if row['claim_status'] == 'Denied':
                    stats["claims"]["denied"] += 1
                    if row['denial_fixable'] == 'True':
                        stats["claims"]["fixable_denials"] += 1
                if row.get('modifier_mismatch') == 'True':
                    stats["claims"]["modifiers"] += 1
                if row.get('denial_risk_flag') == 'True':
                    stats["claims"]["risk_flags"] += 1

    # ROI Analysis
    roi_path = os.path.join(DATA_DIR, "roi_authorizations.csv")
    if os.path.exists(roi_path):
        with open(roi_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats["roi"]["total"] += 1
                if row['auth_expired'] == 'True':
                    stats["roi"]["expired"] += 1

    # Compliance Analysis
    comp_path = os.path.join(DATA_DIR, "compliance_flags.csv")
    if os.path.exists(comp_path):
        with open(comp_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['flag_type'] == 'HIGH_PROVIDER_DENIAL_RATE' and row['metric_value']:
                    stats["compliance"]["denial_rates"].append(float(row['metric_value']))

    # Final Aggregation
    c = stats["claims"]
    r = stats["roi"]
    co = stats["compliance"]
    
    return {
        "claims": {
            "total_count": c["total"],
            "denial_rate_pct": round((c["denied"] / c["total"] * 100), 1) if c["total"] > 0 else 0,
            "preventable_denial_pct": round((c["fixable_denials"] / c["denied"] * 100), 1) if c["denied"] > 0 else 0,
            "modifier_mismatch_pct": round((c["modifiers"] / c["total"] * 100), 1) if c["total"] > 0 else 0,
            "risk_flag_pct": round((c["risk_flags"] / c["total"] * 100), 1) if c["total"] > 0 else 0
        },
        "roi": {
            "total_count": r["total"],
            "expiration_rate_pct": round((r["expired"] / r["total"] * 100), 1) if r["total"] > 0 else 0
        },
        "compliance": {
            "avg_provider_denial_rate_pct": round(sum(co["denial_rates"]) / len(co["denial_rates"]), 1) if co["denial_rates"] else 0
        }
    }

if __name__ == "__main__":
    results = analyze_synthetic_data()
    print(json.dumps(results, indent=2))
