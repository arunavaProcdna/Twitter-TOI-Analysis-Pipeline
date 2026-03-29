# Token counters
import json,os
import pandas as pd
from openai import AzureOpenAI
import json
import time
import os
import logging
import random
from dotenv import load_dotenv
from datetime import datetime




load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key=os.getenv("API_KEY"),
    api_version=os.getenv("API_VERSION")
)

MODEL_NAME = "Auxo_GenAI_Deployment"










total_prompt_tokens = 0
total_completion_tokens = 0

# small delay between calls to prevent bursty behavior (seconds)
PER_CALL_DELAY = float(os.getenv("PER_CALL_DELAY", "0.05"))





# System prompt (unchanged)
system_prompt = """
You are a healthcare analyst reviewing social media posts by healthcare professionals (HCPs). For each post, perform the following tasks:

1. Classify the most appropriate Theme(s) of Interest (TOI) based on the content and intent of the post.
2. You may assign multiple TOIs only if the post clearly supports them. Order them from most prominent to least prominent, separated by commas.

TOI Themes and Inclusion Criteria:

1. Drug Efficacy
    - Use ONLY when the tweet contains quantified clinical results or explicit trial data.
    - Examples: ORR, PFS, OS, CR, DOR, Hb increase with stats, responder rates, comparative efficacy.
    - Do NOT use for Quality of Life (QoL), symptoms, or general “benefit” statements → those go to Patient Outcomes.

2. Safety & Tolerability
    - Tweets discussing adverse events, toxicity grades, dose interruptions due to Adverse Events (AEs), or safety profiles.
    - If Adverse Events (AEs) are mentioned because dose was changed due to toxicity, still → Safety & Tolerability.
    - If no Adverse Events (AEs) mentioned and focus is on dose convenience, → Dosing & Administration.

3. Mechanism of Action & Drug Class Science
    - Science-only content: Mechanism of Action (MoA), molecular targets, pathways, PK/PD, pharmacology, iron metabolism mechanisms, class-level comparisons.
    - No trial results, no approvals, no news, only scientific content.

4. Dosing & Administration
    - Mentions of how a drug is given: route IV/oral, dose frequency, schedule, formulation convenience, infusion times, preparation differences.
    - No Adverse Events (AEs) → Focus is only on how the drug is administered.
    - If adherence, patient burden, or continuation is mentioned → Use Patient Adherence & Compliance.

5. Patient Outcomes
    - Real-world or trial outcomes related to patient experience: QoL, fatigue improvement, symptom improvement, energy levels, recovery, hospitalization avoidance, reduced transfusion need.
    - No numerical trial metrics → otherwise it becomes Drug Efficacy.

6. Patient Adherence & Compliance
    - Mentions of treatment continuation, missed doses, dropping off therapy, regimen complexity, adherence-focused education.
    - If a dose frequency improves/reduces adherence or supports continuation → Patient Adherence & Compliance.
    - But if strictly about how the drug is administered → Dosing & Administration.

7. Patient Support Programs
    - Includes structured support offering: co-pay cards, PAP assistance, nurse navigators, helplines, psychosocial support, reimbursement services.
    - If the tweet only discusses high cost or affordability → Cost & Access.

8. Cost & Access
    - Affordability, reimbursement, health insurance barriers, financial toxicity, access inequality.
    - No mention of structured support programs → Cost & Access.

9. New Developments
    - Announcements of updates: FDA/EMA approvals, label expansions, top-line results, pipeline milestones, new biomarker-driven data, trial initiations.
    - If it's about attending a conference or presenting a poster, not the update itself → Promotional Events.

10. Treatment Guidelines
    - Mentions of NCCN, ESMO, ASH guidelines, recommended pathways, or best-practice treatment algorithms.

11. Disease Awareness
    - Disease burden, epidemiology, prevalence, symptoms, risk factors, community awareness campaigns.
    - If it mentions lack of effective treatments → Unmet Need.

12. Promotional Events
    - Conference invites, booth announcements, poster/oral session promotions, webinars, speaker programs without data or design details.
    - Mentioning a trial name alone without study data.
    - If actual data is discussed → use relevant scientific bucket.

13. General / Non-Scientific
    - Emotional, humorous, congratulatory, team updates, celebration posts, non-clinical statements.
    - No medical or scientific content.

14. Unmet Therapeutic Need
    - Lack of effective treatments, limited options, undertreatment, high unmet need, need for new strategies, gaps in care.
    - If disease burden is mentioned without treatment gaps → Disease Awareness.

Instructions:
- Return only a JSON list of length equal to the number of posts.
- Each item should be a string containing the TOI(s) only.
- If the post is empty, return an empty string for that item.

Example Input:
posts = [
    "New data shows Drug X improves PFS in metastatic breast cancer patients compared to standard therapy.",
    "Reminder: Join our webinar on the latest updates in oncology next week!",
    ""
]

Example Output:
[
    "Drug Efficacy",
    "Promotional Events",
    ""
"""

# ========== FUNCTIONS ==========

def build_prompt(row):
    return f"""
**Input**
Post: {row.get('text', '')}
HCP Twitter Handle: {row.get('twitter_handle_name', '')}
Tweet Status: {row.get('status', '')}
"""

def get_relevance_score(row):
    
    """
    Calls the OpenAI model for a single post and returns the parsed JSON list (or None on failure).
    Implements exponential backoff with jitter to handle rate limits.
    """
    print(f"\n🚀 Calling LLM | text: {row.get('text', '')[:50]}...")
    global total_prompt_tokens, total_completion_tokens
    prompt = build_prompt(row)

    # Tunable parameters
    max_retries = int(os.getenv("MAX_RETRIES", "6"))
    initial_backoff = float(os.getenv("INITIAL_BACKOFF", "2.0"))  # base seconds to wait on first retry
    max_backoff = float(os.getenv("MAX_BACKOFF", "60.0"))  # cap
    attempt = 0

    while attempt <= max_retries:
        try:
            # Small inter-call pause to avoid bursts
            if PER_CALL_DELAY > 0:
                time.sleep(PER_CALL_DELAY)

            response = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0.0,
                max_tokens=100,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            # If we get here, request succeeded
            usage = getattr(response, "usage", None)
            if usage:
                # Some SDK responses provide usage as dict-like
                try:
                    total_prompt_tokens += usage.get("prompt_tokens", 0)
                    total_completion_tokens += usage.get("completion_tokens", 0)
                except Exception:
                    # In case usage is a different structure
                    pass

            output = response.choices[0].message.content.strip()

            # --- SAFE JSON PARSING ---
            start_idx = output.find('[')
            end_idx = output.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_text = output[start_idx:end_idx]
                scores = json.loads(json_text)
                if isinstance(scores, list):
                    return scores

            logging.warning(f"Unexpected or invalid JSON for row {getattr(row, 'name', '')}: {output}")
            return None

        except Exception as e:
            # Convert exception to string for inspection
            err_str = str(e)
            attempt += 1

            # Check for Retry-After header on exception object if present (some libs include response)
            retry_after = None
            try:
                if hasattr(e, "response") and e.response is not None:
                    headers = getattr(e.response, "headers", None)
                    if headers and "Retry-After" in headers:
                        retry_after = float(headers["Retry-After"])
            except Exception:
                retry_after = None

            # If error mentions rate limit or HTTP 429, use exponential backoff logic
            is_rate_limit = False
            if "RateLimit" in err_str or "Rate limit" in err_str or "429" in err_str or "RateLimitReached" in err_str or "Too Many Requests" in err_str:
                is_rate_limit = True

            if is_rate_limit:
                # Use Retry-After if provided
                if retry_after is not None:
                    wait = retry_after
                else:
                    # exponential backoff with jitter
                    backoff = min(max_backoff, initial_backoff * (2 ** (attempt - 1)))
                    jitter = random.uniform(0, backoff * 0.2)
                    wait = backoff + jitter

                logging.warning(f"Rate limit encountered on attempt {attempt}/{max_retries}. Waiting {wait:.2f}s before retry. Error: {err_str}")
                time.sleep(wait)
                continue

            # For other transient errors, also wait but with smaller backoff
            if attempt <= max_retries:
                backoff = min(max_backoff, initial_backoff * (2 ** (attempt - 1)))
                jitter = random.uniform(0, backoff * 0.2)
                wait = backoff + jitter
                logging.error(f"Attempt {attempt}/{max_retries} failed (non-rate-limit). Waiting {wait:.2f}s. Error: {err_str}")
                time.sleep(wait)
                continue

            # If we've exhausted retries, log and return None
            logging.exception(f"All retries exhausted for row {getattr(row, 'name', '')}. Last error: {err_str}")
            return None

    # If somehow we exit loop, return None
    return None
