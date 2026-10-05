from database import save_recommendation
from gemini_utils import engine

def generate_recommendation(user_id, category, data, image_bytes=None, mime_type="image/jpeg"):
    result = engine.generate(category, data, image_bytes, mime_type)
    rec_id = save_recommendation(user_id, category, data, result)
    return rec_id, result
