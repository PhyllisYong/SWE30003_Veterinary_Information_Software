from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health
from app.api.routes import auth
from app.api.routes.content_controller import router as content_router
from app.api.routes import profile

app = FastAPI(title="Vet Info System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(content_router)
app.include_router(profile.router, prefix="/api", tags=["Profile & Pets"])
