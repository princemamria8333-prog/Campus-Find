import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def find_matching_item(lost_item, found_item):

    prompt = f"""
You are CampusFind AI, a campus lost-and-found assistant.

Compare these two reports:

LOST ITEM:
{lost_item}

FOUND ITEM:
{found_item}

Analyze the descriptions, item type and location.

Return your answer in this JSON format:
{{
  "match_score": 85,
  "decision": "Possible Match",
  "reason": "Both items are black wireless earbuds found near the library."
}}

Give a score between 0 and 100.
Do not claim ownership is verified.
Return only valid JSON.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "format": "json"
            },
            timeout=180
        )

        response.raise_for_status()

        result = response.json()
        return json.loads(result["message"]["content"])

    except requests.exceptions.RequestException as error:
        return {"error": f"Ollama connection error: {error}"}

    except (KeyError, ValueError) as error:
        return {"error": f"Could not read AI response: {error}"}