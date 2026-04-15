from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders.ollama import OllamaEncoder
from config import settings
import json
import os
import glob

encoder = OllamaEncoder(name=settings.EMBEDDING_MODEL)
routes = []

if os.path.exists(settings.DIRECTIVES_DIR):
    for filepath in glob.glob(os.path.join(settings.DIRECTIVES_DIR, "*.json")):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                name = os.path.basename(filepath).replace(".json", "")
                phrases = data.get("trigger_phrases", [])
                if phrases:
                    routes.append(Route(name=name, utterances=phrases))
        except Exception as e:
            print(f"[Router] Warning: Failed to load route {filepath}: {e}")

# Initialize the router
route_layer = SemanticRouter(encoder=encoder, routes=routes)


def check_fast_path(user_prompt: str) -> dict | None:
    # --- FIX: If no routes are loaded, the index is not ready. Skip check. ---
    if not route_layer.routes:
        return None

    match = route_layer(user_prompt)
    if match and match.name:
        filepath = os.path.join(settings.DIRECTIVES_DIR, f"{match.name}.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
    return None


def add_new_route(name: str, trigger_phrases: list):
    new_route = Route(name=name, utterances=trigger_phrases)
    route_layer.add(new_route)
