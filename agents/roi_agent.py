from google.adk import Agent
from tools.healthcare_tools import check_roi_status

roi_agent = Agent(
    name="roi_agent",
    instruction="""
    Purpose: Determine whether the caller is acting on behalf of another adult member.
    
    If ROI is missing or expired:
    - explain privacy restrictions (HIPAA)
    - explain why information cannot be released
    - recommend how to submit ROI
    - route appropriately
    
    Use check_roi_status() to verify if the caller has authorization.
    """,
    tools=[check_roi_status]
)
