# Research-Based Business Impact Assumptions

## Call Timing Benchmarks
- **Average Handle Time (AHT) - Healthcare:** 
  - Industry average: **6.6 minutes** (396s)
  - Complex inquiries (Claims/Clinical/Billing): **10 - 15 minutes** (600s - 900s)
  - *Source: Spinsci.ai (2024), Dialog Health (2025)*
- **First Call Resolution (FCR):** 
  - Industry average: **52%**
  - AI-Enabled Target: **75% - 85%**
  - *Source: Dialog Health (2024)*
- **After-Call Work (ACW) Reduction:** 
  - Generative AI can reduce documentation and summary time by up to **80%**.
  - *Source: Industry Benchmarks for Agent Assist AI (2024)*

## Financial Benchmarks
- **Fully Burdened Agent Cost:** 
  - Range: **$25 - $45 per hour**
  - Includes: Base wage ($18-21), payroll taxes, benefits, IT overhead, and training.
  - *Source: Callforce Global, SymTrain (2024/2025)*

## Workflow Timing Assumptions (seconds)
*Calculations below are based on a "Complex Claim/Coverage Inquiry" (10-minute traditional baseline).*

| Stage | Traditional | AI-Assisted | Rationale |
| :--- | :--- | :--- | :--- |
| Member verification | 45 | 10 | AI automates ID/V via voice/context. |
| Claim lookup | 60 | 5 | AI retrieves data via backend API instantly. |
| Coverage lookup | 90 | 15 | AI performs semantic search over policy docs. |
| Prior auth verification | 120 | 20 | AI cross-references clinical rules/status. |
| ROI verification | 45 | 5 | Automated check against authorization DB. |
| Claim explanation | 180 | 45 | AI generates concise, clear benefit summaries. |
| Recommended next actions | 60 | 10 | AI maps policy rules to specific next steps. |
| **Total AHT** | **600s (10m)** | **110s (1.8m)** | **~82% Reduction in handle time.** |

## Financial ROI Model
- **Annual Call Volume:** 1,200,000 (Conservative estimate for a Humana-scale specialized desk)
- **Cost per Second:** $0.0116 ($42/hr fully burdened)
- **Estimated Annual Savings:** ~$6.86M (Direct labor savings only)

## Synthetic Dataset Insights (Project-Specific)
*Derived from analysis of 880+ claim records and 350+ ROI records:*
- **Claim Denial Rate:** **24.1%**
- **Preventable (Fixable) Denials:** **73.6%** of all denied claims were flagged as "fixable," representing a major opportunity for AI-assisted correction.
- **ROI Friction:** **12.2%** of member ROIs are currently expired, leading to significant authentication hold times and manual verification steps.
- **Provider Performance:** High-denial-risk providers average a **38.6%** denial rate, justifying the need for AI-driven proactive compliance monitoring.

## Unstructured Data Insights (Transcripts & Reports)
*Derived from analysis of 12 call transcripts and the Q1/Q2 STARs Performance Report:*
- **Handle Time Reality:** Transcripts confirm an average call duration of **6.4 minutes (385s)**, with complex denial inquiries reaching **12 minutes (720s)**.
- **Top Friction Scenarios:**
  1. **Coordination of Benefits (COB):** High complexity explanations (e.g., CO-109) drive longer "Discovery" phases.
  2. **Missing ROI:** Leads to immediate "hard stops" in 16% of transcript scenarios, causing member frustration and repeat calls.
- **STARs Rating Opportunity:** 8 of 8 scored measures are currently "At Risk" (1-2 Stars). 
  - **Gap Closure Impact:** Closing just 40% of open gaps in Blood Pressure (CBP) could improve ratings by up to **4 percentage points**.
  - **AI Value:** Automating Care Gap outreach (Scenarios 03/09 in transcripts) can reduce outbound handle time from **8 minutes to <2 minutes**, enabling 4x higher outreach volume.
