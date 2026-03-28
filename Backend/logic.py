import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key="rc_fac7e1cbaa917838108fb4d75c5276677ee11f86344092cffae3a79510bf00e6",
)


def process_complaint(text, student_name):
    try:
        if len(text.strip().split()) < 3:
            return {
                "category": "Invalid",
                "status": "Rejected",
                "assigned_to": "None",
                "response": "Complaint too short",
                "letter": f"Complaint too short.\n\nRegards,\n{student_name}"
            }

        # 🔥 AI classification
        prompt = f"""
You are an intelligent university complaint system.

STRICT FORMAT:

VALID: YES or NO

If VALID = YES:
CATEGORY: Academic | Hostel | Infrastructure | Discipline
STATUS: Auto-resolved or Escalated
ASSIGNED_TO: dean | warden | it_head | security
RESPONSE: Detailed explanation (minimum 3 lines)

Complaint: {text}
"""

        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        output = response.choices[0].message.content.strip()

        # 🔥 Parse output
        data = {}
        for line in output.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()

        if data.get("VALID", "NO") == "NO":
            reason = data.get("REASON", "Invalid complaint")
            return {
                "category": "Invalid",
                "status": "Rejected",
                "assigned_to": "None",
                "response": reason,
                "letter": f"{reason}\n\nRegards,\n{student_name}"
            }

        # 🔥 Category mapping (FIXED)
        raw = data.get("CATEGORY", "").lower()

        if "academic" in raw:
            category = "Academic Issues"
        elif "hostel" in raw:
            category = "Hostel Issues"
        elif "infrastructure" in raw or "wifi" in raw or "computer" in raw or "internet" in raw:
            category = "Infrastructure"
        elif "discipline" in raw:
            category = "Discipline"
        else:
            category = "Infrastructure"   # fallback

        status = data.get("STATUS", "Pending")
        assigned = data.get("ASSIGNED_TO", "").strip().lower()
        message = data.get("RESPONSE", output)

        # 🔥 Role mapping FIX
        role_map = {
            "Academic Issues": "dean",
            "Hostel Issues": "warden",
            "Infrastructure": "it_head",
            "Discipline": "security"
        }

        if assigned not in role_map.values():
            assigned = role_map.get(category, "dean")

        # 🔥 AI LETTER GENERATION
        letter_prompt = f"""
Write a formal complaint letter from a student named {student_name}.

Complaint: {text}
Explanation: {message}

Instructions:
- Address to {assigned}
- Minimum 6–8 lines
- Natural human tone
- Polite and respectful
- Ask for resolution clearly
"""

        letter_res = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": letter_prompt}],
            temperature=0.6
        )

        letter = letter_res.choices[0].message.content.strip()

        return {
            "category": category,
            "status": status,
            "assigned_to": assigned,
            "response": message,
            "letter": letter
        }

    except Exception as e:
        print("ERROR:", e)

        return {
            "category": "Unknown",
            "status": "Pending",
            "assigned_to": "dean",
            "response": "System unavailable",
            "letter": f"System failed. Please try again.\n\nRegards,\n{student_name}"
        }