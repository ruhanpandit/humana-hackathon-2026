from google.adk import Agent
from tools.healthcare_tools import calculate_claim_risk, lookup_claim, lookup_provider

compliance_agent = Agent(
    name="compliance_agent",
    instruction="""
    Purpose: Analyze operational signals and detect risks.
    
    Detect:
    - repeated denial trends
    - modifier errors
    - referral issues
    - eligibility failures
    - provider anomalies
    - compliance concerns
    
    Return alerts and recommended preventive actions.
    Use calculate_claim_risk() to get an automated risk assessment.
    Use lookup_claim() and lookup_provider() for additional context if needed.
    """,
    tools=[calculate_claim_risk, lookup_claim, lookup_provider]
)
