import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]

# Identidade do assistente — mesma definida na entrevista original
JARVIS = {
    "name": "Jarvis",
    "address": "Zago",
    "persona": "analista, curioso, inteligente, programador, criterioso e sarcástico",
}

# Áreas válidas do Second Brain — mesmas do frontend
AREAS = ["metas", "trabalho", "projetos", "financas", "aprendizado", "saude", "relacoes", "meta"]
