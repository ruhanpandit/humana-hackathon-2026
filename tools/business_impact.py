import yaml
import os

def load_config():
    """Loads the workflow and impact assumptions from the configuration file."""
    # Assuming the config is in ../config/workflow_config.yaml relative to this file
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'workflow_config.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Fallback defaults if config is missing
        return {
            "workflow_stages": {
                "member_verification": {"traditional": 45, "ai_assisted": 10},
                "claim_lookup": {"traditional": 60, "ai_assisted": 5},
                "coverage_lookup": {"traditional": 90, "ai_assisted": 15},
                "prior_auth_verification": {"traditional": 120, "ai_assisted": 20},
                "roi_verification": {"traditional": 45, "ai_assisted": 5},
                "claim_explanation": {"traditional": 180, "ai_assisted": 45},
                "recommended_next_actions": {"traditional": 60, "ai_assisted": 10}
            },
            "impact_assumptions": {
                "fcr_improvement_pct": 22,
                "repeat_call_reduction_pct": 18,
                "preventable_denials_reduction_pct": 15,
                "annual_call_volume": 1200000,
                "cost_per_second": 0.02
            }
        }

def calculate_business_impact():
    """
    Calculates all business impact metrics based on configurable assumptions.
    Returns a dictionary structured for easy consumption by a dashboard.
    """
    config = load_config()
    stages = config['workflow_stages']
    impact = config['impact_assumptions']
    
    total_traditional = 0
    total_ai = 0
    comparison_data = []
    
    # Requirement 1 & 2: Process stages and handle times
    for stage_key, times in stages.items():
        trad = times['traditional']
        ai = times['ai_assisted']
        total_traditional += trad
        total_ai += ai
        comparison_data.append({
            "stage": stage_key.replace('_', ' ').title(),
            "traditional": trad,
            "ai_assisted": ai,
            "saved": trad - ai,
            "reduction_pct": round(((trad - ai) / trad * 100), 1) if trad > 0 else 0
        })
        
    # Requirement 3: Calculations
    time_saved_per_call = total_traditional - total_ai
    aht_reduction_pct = (time_saved_per_call / total_traditional) * 100 if total_traditional > 0 else 0
    
    annual_volume = impact['annual_call_volume']
    cost_per_sec = impact['cost_per_second']
    
    total_annual_hours_saved = (time_saved_per_call * annual_volume) / 3600
    total_annual_financial_savings = time_saved_per_call * annual_volume * cost_per_sec
    
    # Requirement 4 & 5: Return structured data for KPIs and Charts
    return {
        "kpis": [
            {
                "label": "Average Handle Time Saved",
                "value": f"{round(aht_reduction_pct, 1)}%",
                "delta": "vs Traditional",
                "description": "Reduction in total interaction time"
            },
            {
                "label": "Time Saved Per Call",
                "value": f"{time_saved_per_call}s",
                "delta": f"-{round(aht_reduction_pct, 1)}%",
                "description": "Total seconds saved per interaction"
            },
            {
                "label": "First Call Resolution Improvement",
                "value": f"+{impact['fcr_improvement_pct']}%",
                "delta": "Estimated",
                "description": "Projected increase in single-interaction resolution"
            },
            {
                "label": "Repeat Call Reduction",
                "value": f"-{impact['repeat_call_reduction_pct']}%",
                "delta": "Estimated",
                "description": "Projected decrease in follow-up inquiries"
            },
            {
                "label": "Preventable Denials Reduction",
                "value": f"-{impact['preventable_denials_reduction_pct']}%",
                "delta": "Estimated",
                "description": "Reduction in administrative errors"
            },
            {
                "label": "STARs Gap Closure Improvement",
                "value": f"+{impact['stars_gap_closure_improvement']} pp",
                "delta": "Target",
                "description": "Projected improvement in key STARs measures"
            }
        ],
        "financials": {
            "annual_hours_saved": round(total_annual_hours_saved, 0),
            "annual_financial_savings": round(total_annual_financial_savings, 2),
            "cost_reduction_pct": round(aht_reduction_pct, 1)
        },
        "workflow_comparison": {
            "traditional_total": total_traditional,
            "ai_total": total_ai,
            "stages": comparison_data
        }
    }

if __name__ == "__main__":
    import json
    results = calculate_business_impact()
    print(json.dumps(results, indent=2))
