import json
from urllib.parse import quote_plus
from config import settings

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

PLATFORMS = {
    "amazon": "https://www.amazon.in/s?k={q}",
    "flipkart": "https://www.flipkart.com/search?q={q}",
    "ikea": "https://www.ikea.com/in/en/search/?q={q}",
    "swiggy": "https://www.swiggy.com/search?query={q}",
    "zomato": "https://www.zomato.com/search?q={q}",
    "oyo": "https://www.oyorooms.com/search?q={q}",
    "booking": "https://www.booking.com/searchresults.html?ss={q}",
    "myntra": "https://www.myntra.com/{q}",
    "tanishq": "https://www.tanishq.co.in/search?q={q}",
    "bluestone": "https://www.bluestone.com/search.html?q={q}",
}

class GeminiRecommendationEngine:
    def __init__(self):
        self.client = None
        if genai and settings.gemini_api_key:
            try:
                self.client = genai.Client(api_key=settings.gemini_api_key)
            except Exception:
                self.client = None

    def _platform_links(self, item, platforms):
        q = quote_plus(item.get("search_terms") or item.get("name") or "")
        return {p: PLATFORMS[p].format(q=q) for p in platforms if p in PLATFORMS}

    def _fallback(self, category, data):
        budget = float(data.get("total_budget", 0))
        if category == "home":
            items = [
                {"category":"Lighting","name":"LED Ceiling Light","description":"Energy-efficient modern ceiling light","estimated_price":max(800, budget*0.08),"quantity":data.get("lights",1),"search_terms":"modern LED ceiling light"},
                {"category":"Furniture","name":"Compact Sofa","description":"Practical sofa for a modern room","estimated_price":max(6000, budget*0.28),"quantity":data.get("furniture",1),"search_terms":"modern compact sofa"},
                {"category":"Fan","name":"Energy Efficient Ceiling Fan","description":"Reliable ceiling fan for everyday use","estimated_price":max(2200, budget*0.10),"quantity":data.get("fans",1),"search_terms":"energy efficient ceiling fan"},
            ]
            platforms = ["amazon", "flipkart", "ikea"]
        elif category == "party":
            items = [
                {"category":"Catering","name":"Party Food Package","description":"Budget-friendly catering package","estimated_price":budget*0.40,"quantity":1,"search_terms":f"{data.get('party_type','party')} catering {data.get('guests',10)} guests"},
                {"category":"Decoration","name":"Event Decoration Package","description":"Theme-based decoration package","estimated_price":budget*0.20,"quantity":1,"search_terms":f"{data.get('party_type','party')} decoration"},
                {"category":"Venue","name":"Event Venue","description":"Venue options suitable for the guest count","estimated_price":budget*0.30,"quantity":1,"search_terms":f"event venue {data.get('guests',10)} guests"},
            ]
            platforms = ["swiggy", "zomato", "oyo", "booking"]
        else:
            items = [
                {"item_type":"Necklace Set","description":"Elegant occasion-friendly necklace","style":data.get("preferences","Elegant"),"estimated_price":budget*0.35,"search_terms":"elegant necklace set"},
                {"item_type":"Earrings","description":"Matching earrings for the selected occasion","style":data.get("preferences","Elegant"),"estimated_price":budget*0.20,"search_terms":"occasion earrings"},
                {"item_type":"Bangles","description":"Coordinated bangle set","style":data.get("preferences","Elegant"),"estimated_price":budget*0.15,"search_terms":"designer bangles set"},
            ]
            platforms = ["amazon", "flipkart", "tanishq", "bluestone"]
        total = sum(float(i.get("estimated_price",0)) * int(i.get("quantity",1)) for i in items)
        for item in items:
            item["shopping_links"] = self._platform_links(item, platforms)
        return {"total_budget": budget, "budget_breakdown": items, "remaining_budget": max(0, budget-total), "source":"Local fallback recommendations", "note":"Add GEMINI_API_KEY in .env to enable Gemini-generated recommendations."}

    def _prompt(self, category, data):
        common = f"""You are PocketSmart AI, a budget recommendation assistant for India. Return valid JSON only. All prices must be in INR and the total estimated cost must not exceed the user's budget. Recommend practical options and include platform search terms. User data: {json.dumps(data, ensure_ascii=False)}."""
        if category == "home":
            return common + " Generate home interior recommendations for rooms, lighting, fans, furniture and dining requirements. JSON keys: total_budget, budget_breakdown (array of category,name,description,estimated_price,quantity,search_terms), remaining_budget, styling_tips."
        if category == "party":
            return common + " Generate party planning recommendations for venue, catering, decoration and entertainment according to event type and guest count. JSON keys: total_budget, budget_breakdown (array of category,name,description,estimated_price,quantity,search_terms), venue_suggestions, remaining_budget, planning_tips."
        return common + " Generate jewelry recommendations for the occasion and style, optionally considering outfit description/image. JSON keys: total_budget, outfit_analysis, jewelry_recommendations (array of item_type,description,style,estimated_price,search_terms), remaining_budget, styling_tips."

    def generate(self, category, data, image_bytes=None, mime_type="image/jpeg"):
        if not self.client:
            return self._fallback(category, data)
        try:
            prompt = self._prompt(category, data)
            contents = [prompt]
            if image_bytes and types:
                contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
                contents.append("Analyze the outfit image for colors, style and occasion suitability, but do not identify the person.")
            response = self.client.models.generate_content(model=settings.gemini_model, contents=contents)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.replace("```json", "", 1).replace("```", "").strip()
            result = json.loads(text)
            result["source"] = f"Gemini model: {settings.gemini_model}"
            self._add_links(result, category)
            return result
        except Exception as exc:
            fallback = self._fallback(category, data)
            fallback["ai_error"] = str(exc)
            return fallback

    def _add_links(self, result, category):
        if category == "jewelry":
            items = result.get("jewelry_recommendations", [])
            platforms = ["amazon", "flipkart", "tanishq", "bluestone"]
        elif category == "party":
            items = result.get("budget_breakdown", [])
            platforms = ["swiggy", "zomato", "oyo", "booking"]
        else:
            items = result.get("budget_breakdown", [])
            platforms = ["amazon", "flipkart", "ikea"]
        for item in items:
            item["shopping_links"] = self._platform_links(item, platforms)

engine = GeminiRecommendationEngine()
