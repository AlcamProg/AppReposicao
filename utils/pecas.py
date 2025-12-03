import json

def carregar_base_pecas():
    with open("pecas/pecas.json", "r", encoding="utf-8") as f:
        return json.load(f)
