import json
from pathlib import Path
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from auth import hash_password, verify_password, create_access_token, current_user, require_user
from database import create_user, get_user_by_email, get_recommendation, list_history
from recommendation_service import generate_recommendation
from schemas import RegisterRequest, LoginRequest, HomeRequest, PartyRequest, JewelryRequest

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def render(request, name, **context):
    context["user"] = current_user(request)
    return templates.TemplateResponse(request=request, name=name, context=context)

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render(request, "index.html")

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return render(request, "register.html")

@router.post("/register")
def register(request: Request, email: str = Form(...), full_name: str = Form(...), password: str = Form(...)):
    try:
        data = RegisterRequest(email=email, full_name=full_name, password=password)
    except ValidationError as e:
        return render(request, "register.html", error=e.errors()[0]["msg"])
    if get_user_by_email(data.email):
        return render(request, "register.html", error="Email already registered.")
    user_id = create_user(data.email, data.full_name, hash_password(data.password))
    token = create_access_token(user_id, data.email)
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=3600)
    return response

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render(request, "login.html")

@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return render(request, "login.html", error="Invalid email or password.")
    token = create_access_token(user["id"], user["email"])
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=3600)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.post("/token")
def token(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        return JSONResponse({"detail":"Incorrect email or password"}, status_code=401)
    return {"access_token": create_access_token(user["id"], user["email"]), "token_type":"bearer"}

@router.get("/session-info")
def session_info(request: Request):
    user = current_user(request)
    if not user:
        return {"logged_in":False}
    return {"logged_in":True,"user_id":user["id"],"email":user["email"],"full_name":user["full_name"]}

@router.get("/session-data")
def session_data(request: Request):
    user = require_user(request)
    history = list_history(user["id"])
    return {"user_id":user["id"],"recommendation_count":len(history)}

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = require_user(request)
    history = list_history(user["id"])
    return render(request, "dashboard.html", history=history[:5])

@router.get("/home-planner", response_class=HTMLResponse)
def home_planner(request: Request):
    require_user(request)
    return render(request, "home_planner.html")

@router.post("/generate-home", response_class=HTMLResponse)
def generate_home(request: Request, total_budget: float = Form(...), rooms: str = Form(...), lights: int = Form(1), fans: int = Form(1), furniture: int = Form(1), dining_tables: int = Form(0), style: str = Form("Modern"), additional_requirements: str = Form("")):
    user = require_user(request)
    data = HomeRequest(total_budget=total_budget, rooms=rooms, lights=lights, fans=fans, furniture=furniture, dining_tables=dining_tables, style=style, additional_requirements=additional_requirements).model_dump()
    rec_id, result = generate_recommendation(user["id"], "home", data)
    return render(request, "recommendations.html", category="Home Interior", result=result, rec_id=rec_id)

@router.get("/party-planner", response_class=HTMLResponse)
def party_planner(request: Request):
    require_user(request)
    return render(request, "party_planner.html")

@router.post("/generate-party", response_class=HTMLResponse)
def generate_party(request: Request, total_budget: float = Form(...), party_type: str = Form(...), guests: int = Form(...), venue_type: str = Form("Not specified"), catering: bool = Form(False), decoration: bool = Form(False), entertainment: bool = Form(False), additional_requirements: str = Form("")):
    user = require_user(request)
    data = PartyRequest(total_budget=total_budget, party_type=party_type, guests=guests, venue_type=venue_type, catering=catering, decoration=decoration, entertainment=entertainment, additional_requirements=additional_requirements).model_dump()
    rec_id, result = generate_recommendation(user["id"], "party", data)
    return render(request, "recommendations.html", category="Party Planning", result=result, rec_id=rec_id)

@router.get("/jewelry-planner", response_class=HTMLResponse)
def jewelry_planner(request: Request):
    require_user(request)
    return render(request, "jewelry_planner.html")

@router.post("/generate-jewelry", response_class=HTMLResponse)
async def generate_jewelry(request: Request, total_budget: float = Form(...), occasion: str = Form(...), preferences: str = Form(...), outfit_description: str = Form(""), outfit_image: UploadFile | None = File(None)):
    user = require_user(request)
    image_bytes = None
    image_name = None
    mime_type = "image/jpeg"
    if outfit_image and outfit_image.filename:
        image_bytes = await outfit_image.read()
        image_name = outfit_image.filename
        mime_type = outfit_image.content_type or "image/jpeg"
    data = JewelryRequest(total_budget=total_budget, occasion=occasion, preferences=preferences, outfit_description=outfit_description, image_name=image_name).model_dump()
    rec_id, result = generate_recommendation(user["id"], "jewelry", data, image_bytes, mime_type)
    return render(request, "recommendations.html", category="Jewelry Recommendations", result=result, rec_id=rec_id)

@router.get("/recommendations-details/{rec_id}", response_class=HTMLResponse)
def recommendation_details(request: Request, rec_id: int):
    user = require_user(request)
    rec = get_recommendation(user["id"], rec_id)
    if not rec:
        return render(request, "error.html", message="Recommendation not found.")
    return render(request, "recommendations.html", category=rec["category"].title(), result=json.loads(rec["result_data"]), rec_id=rec_id)

@router.get("/history", response_class=HTMLResponse)
def history(request: Request):
    user = require_user(request)
    return render(request, "history.html", history=list_history(user["id"]))

@router.get("/api/health")
def health():
    return {"status":"ok","service":"PocketSmart AI"}
