from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, forget
from app.core.logging_config import setup_logging
from app.core.database import init_db

def get_application() -> FastAPI:
    # 初始化日志系统
    setup_logging()
    
    # 初始化数据库
    init_db()
    
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
    application.include_router(auth.router)
    application.include_router(forget.router)

    return application

app = get_application()

@app.get("/")
async def root():
    return {
        "message": "Welcome to FWWB A12 Auth API",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "endpoints": [
            "/api/v1/login (POST) - User Login",
            "/api/v1/register/student (POST) - Student Registration",
            "/api/v1/register/teacher (POST) - Teacher Registration",
            "/api/v1/register/send-code (POST) - Send Verification Code",
            "/api/v1/register/verify-code (POST) - Verify Verification Code"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("auth_server:app", host="0.0.0.0", port=8000, reload=True)
