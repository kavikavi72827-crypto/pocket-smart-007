# Source Alignment Notes

This implementation was created from the supplied 39-page PocketSmart AI specification.

Implemented items from the specification:
- Budget-aware Home Interior, Party, and Jewelry planners.
- Gemini integration with optional multimodal image input for Jewelry.
- FastAPI modular backend and Jinja2 HTML frontend.
- `/generate-home`, `/generate-party`, `/generate-jewelry`.
- `/register`, `/login`, `/logout`, `/token`.
- `/session-info`, `/session-data`, `/history`, and recommendation details.
- CORS-ready modular architecture can be extended for a separate frontend.
- Platform-specific search links for Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO and other platforms described in the specification.
- Local fallback recommendations so the project remains runnable when a Gemini API key is not configured.
- SQLite persistence for users and recommendation history.

The specification mentions Flask in its early architecture/workflow text and FastAPI in the backend milestone and conclusion. This runnable implementation follows the later FastAPI architecture because it explicitly defines the backend routes, startup, Uvicorn entry point, and Jinja2 integration.

The third-party shopping platforms are represented as search links rather than undocumented scraping or private APIs. This keeps the project runnable and avoids requiring platform-specific credentials.
