from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders.ollama import OllamaEncoder
from config import settings
import json
import os
import glob

# Initialize encoder
encoder = OllamaEncoder(name=settings.EMBEDDING_MODEL)
routes = []

# 1. Load existing routes from disk
if os.path.exists(settings.DIRECTIVES_DIR):
    json_files = glob.glob(os.path.join(settings.DIRECTIVES_DIR, "*.json"))
    print(f"🔧 [Router] Found {len(json_files)} directive files on disk.")

    for filepath in json_files:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                name = os.path.basename(filepath).replace(".json", "")
                phrases = data.get("trigger_phrases", [])
                if phrases:
                    routes.append(Route(name=name, utterances=phrases))
                    print(f"   Loaded route: {name} ({len(phrases)} phrases)")
        except Exception as e:
            print(f"   ❌ Warning: Failed to load route {filepath}: {e}")

# 2. Initialize the router with loaded routes
route_layer = SemanticRouter(encoder=encoder, routes=routes)


def check_fast_path(user_prompt: str) -> dict | None:
    # --- STABILITY CHECK 1: No routes loaded? Skip. ---
    if not route_layer.routes:
        return None

    try:
        # --- STABILITY CHECK 2: Is the index actually ready? ---
        if route_layer.index is None:
            return None

        match = route_layer(user_prompt)

        if match and match.name:
            filepath = os.path.join(settings.DIRECTIVES_DIR, f"{match.name}.json")
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    print(f"⚡ [Autopilot] Match found: {match.name}")
                    return json.load(f)

    except Exception as e:
        # --- STABILITY CHECK 3: Any router-specific error (like "Index not ready") ---
        # We log it and return None to let the Pilot (LLM) handle the request
        print(f"⚠️ [Router] Skipping fast-path check due to internal state: {e}")
        return None

    return None


def add_new_route(name: str, trigger_phrases: list):
    try:
        new_route = Route(name=name, utterances=trigger_phrases)
        route_layer.add(new_route)
        print(f"✅ [Router] New route '{name}' indexed.")
    except Exception as e:
        print(f"❌ [Router] Failed to add new route: {e}")
