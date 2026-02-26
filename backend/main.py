from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.v1 import chat, student

def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include Routers
    application.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    application.include_router(student.router, prefix="/api/v1/student", tags=["student"])

    return application

app = get_application()

@app.get("/")
async def root():
    return {
        "message": "Welcome to FWWB A12 API (Role D: QA & Teacher Agent)",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "endpoints": [
            "/api/v1/chat/chat (POST) - Main QA/Teacher Interface",
            "/api/v1/chat/session/start (POST) - Start Learning/Preview",
            "/api/v1/chat/session/{id}/preview (GET) - Check Video Generation",
            "/api/v1/student/profile (GET/POST) - Manage Student Profile"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
