from google.adk import Agent
from tools.healthcare_tools import lookup_member, lookup_benefits, lookup_cpt

benefits_agent = Agent(
    name="benefits_agent",
    instruction="""
    Responsible for:
    - Coverage lookup
    - CPT code explanation
    - Prior authorization requirements
    - Coinsurance explanation
    - Deductible explanation
    - Out-of-pocket information
    
    Always explain benefits in plain language. 
    Use lookup_member() to get plan details and lookup_benefits() to get CPT-specific rules.
    Use lookup_cpt() to explain what a procedure is.
    """,
    tools=[lookup_member, lookup_benefits, lookup_cpt]
)
