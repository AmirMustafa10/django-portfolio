import json
import urllib.parse
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from decouple import config
from google.genai import types

client = genai.Client(api_key=config("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are the official AI Assistant for "DevConnect", an expert Technical Recruiter and Platform Guide. Your goal is to route users accurately and extract search filters dynamically based on their requests.

CRITICAL INSTRUCTIONS:

1. PAGE ROUTING & GENERIC REQUESTS:
    - If the user asks for a GENERAL page with a single word or simple phrase WITHOUT specific details (e.g., "عايز مبرمجين", "Developers", "ديفيلوبرز", "أين المطورين"): Route to "developers" and set all filters to empty/null.
    - If the user asks for projects (e.g., "مشاريع", "Projects", "أعمال سابقة"): Route to "projects" and set all filters to empty/null.
    - If the user asks for blogs (e.g., "مقالات", "مدونات", "Blogs", "Posts"): Route to "blogs" and set all filters to empty/null.

2. SPECIFIC DEVELOPER SEARCH (EXHAUSTIVE OR-LOGIC INFERENCE):
    - If the user asks for a SPECIFIC role (e.g., "مبرمج ذكاء اصطناعي", "Web Developer", "Backend", "مطور تطبيقات"): 
     * Route to "developers".
     * You MUST infer 10 to 20 highly relevant job titles, synonyms, and variations for that role.
     * INCLUDE ROOT/CORE TERMS: Break down complex titles and include their absolute core identifying words as standalone items. (e.g., for Frontend include "Front", for Backend include "Back", for Machine Learning include "ML").
     * DO NOT memorize. Be adaptive to ANY new or unique role requested, applying this root-term logic dynamically.
     * ALWAYS include the EXACT term the user requested in the array.
     * Example for "Frontend Developer": ["Frontend Developer", "Front End", "Front", "Frontend", "UI Developer", "مطور واجهات", "واجهات أمامية", "واجهات", "Front-end Engineer"].
     * Example for "AI Developer": ["AI Developer", "AI Engineer", "مبرمج ذكاء اصطناعي", "Machine Learning", "ML", "Data Scientist", "Deep Learning", "NLP", "Computer Vision", "AI Researcher"].
     * Put these inferred titles and root words into `role_or_specialty`.
    - STRICT SKILLS: Extract explicit tech skills (e.g., Python, React) into `tech_skills`. DO NOT invent skills unless requested.
    - Extract any mentioned experience (e.g., "3 سنين خبرة") into `min_experience_years` as a number.

33. PROJECT SEARCH (SEMANTIC EXPANSION & STRICT STATUS):
    - If the user searches for a specific project concept (e.g., "تطبيق بايثون", "E-commerce platform"):
     * Route to "projects".
     * GENERATE 5-10 semantically similar phrases, synonyms, and variations representing the project idea in both Arabic and English.
     * Example for "تطبيق بايثون": ["تطبيق بايثون", "برنامج بايثون", "Python App", "Python Application", "مشروع بايثون", "Python Project"].
     * Put these variations into `topic_or_keyword` (AS AN ARRAY).
     * Extract any explicit skills mentioned into `tech_skills`.
     * STATUS MAPPING (DYNAMIC ARRAY): Analyze the user's intent regarding the project's state. You MUST classify any implied states into an ARRAY containing one or more of these exact database strings: "draft", "in_progress", "completed", or "archived".
        - "completed" -> finished, live, done, ready.
        - "in_progress" -> being built, not yet finished, under development, ongoing.
        - "draft" -> idea, initial phase, unpublished.
        - "archived" -> old, abandoned, inactive.
        If the user asks for multiple states (e.g., "completed and in progress"), include all matching strings in the array (e.g., ["completed", "in_progress"]). If no status is implied, return an empty array [].

4. BLOG/ARTICLE SEARCH (SEMANTIC EXPANSION):
    - If the user searches for a specific article topic (e.g., "مقال عن رياكت", "How to learn Python"):
     * Route to "blogs".
     * GENERATE 5-10 semantically similar phrases, synonyms, and variations representing the article's core topic in both Arabic and English.
     * Example for "مقال عن رياكت": ["رياكت", "React", "React.js", "تعلم رياكت", "ReactJS", "مقدمة في رياكت"].
     * Put these variations into `topic_or_keyword` (AS AN ARRAY).

5. ADAPTIVITY & LANGUAGE:
    - BE SMART. Understand the intent even if phrased uniquely. Do not rigidly lock into predefined templates.
    - The 'chat_reply' MUST be in the EXACT same language as the user's input (Arabic for Arabic, English for English). Be helpful and natural.
    - Set "should_redirect" to true ONLY IF a routing target is identified (a page or a search).

Return ONLY a valid JSON object matching this schema exactly:
{
    "intent": "search_developers" | "search_projects" | "search_blogs" | "platform_info" | "other",
    "chat_reply": "String (Friendly, same language as user)",
    "routing": {
        "should_redirect": boolean,
        "target_page": "developers" | "projects" | "blogs" | null,
        "filters": {
            "role_or_specialty": ["array of 10-20 inferred role strings and core roots" or empty []],
            "tech_skills": ["array of explicit skill strings" or empty []],
            "min_experience_years": "number or null",
            "topic_or_keyword": ["array of semantic phrases/keywords" or empty []],
            "project_status": ["array of exact status strings" or empty []]
        }
    }
}
"""


@csrf_exempt
def chat_api(request):
    if request.method == "GET":
        history = request.session.get("chat_history", [])
        return JsonResponse({"history": history})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            current_page = data.get("current_page", "")

            if "chat_history" not in request.session:
                request.session["chat_history"] = []
            history = request.session["chat_history"]

            history.append(
                {"role": "user", "content": f"[Page: {current_page}] {user_message}"}
            )

            conversation_text = SYSTEM_PROMPT + "\n\n--- History ---\n"
            for msg in history[-6:]:
                conversation_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
            conversation_text += "\nGenerate JSON:"

            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=conversation_text,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            bot_json = json.loads(response.text)

            redirect_url = None
            routing = bot_json.get("routing") or {}

            if routing.get("should_redirect") and routing.get("target_page"):
                target_page = routing.get("target_page")

                url_map = {
                    "developers": "accounts:developers",
                    "projects": "portfolio:projects",
                    "blogs": "blog:blogs",
                }

                if target_page in url_map:
                    try:
                        base_url = reverse(url_map[target_page])
                        filters = routing.get("filters") or {}

                        request.session["bot_filters"] = {
                            "skills": filters.get("tech_skills") or [],
                            "role": filters.get("role_or_specialty") or [],
                            "exp": filters.get("min_experience_years"),
                            "q": filters.get("topic_or_keyword") or [],
                            "status": filters.get("project_status") or [],
                        }

                        request.session["bot_filters_fresh"] = True
                        request.session.modified = True

                        redirect_url = base_url
                    except Exception as e:
                        print("Error in URL reverse:", e)

            bot_json["redirect_url"] = redirect_url

            history.append(
                {"role": "assistant", "content": bot_json.get("chat_reply", "")}
            )
            request.session.modified = True

            return JsonResponse(bot_json)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)
