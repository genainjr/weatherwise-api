from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="WeatherWise API",
    description="API inteligente de recomendações climáticas",
    version="1.0.0"
)

# CORS para frontend acessar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "WeatherWise API",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Seus endpoints vão aqui
@app.get("/api/weather/current/{city}")
def get_current_weather(city: str):
    # TODO: Implementar
    return {"city": city, "temp": 28}