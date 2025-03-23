from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()
MODASH_API_KEY = os.environ.get("MODASH_API_KEY")

PLATFORM_ENDPOINTS = {
    "instagram": "https://api.modash.io/v1/instagram/search",
    "tiktok": "https://api.modash.io/v1/tiktok/search",
    "youtube": "https://api.modash.io/v1/youtube/search"
}

HEADERS = {
    "Authorization": f"Bearer {MODASH_API_KEY}",
    "Content-Type": "application/json"
}

def create_payload(query: str):
    # This is placeholder logic. In a real application, you'd parse the query intelligently.
    payload = {
        "page": 0,
        "filter": {
            "influencer": {
                "followers": {
                    "gte": 50000
                }
            }
        },
        "sort": {
            "direction": "desc",
            "field": "followers"
        }
    }

    if "beauty" in query.lower():
        payload["filter"]["influencer"]["topics"] = ["beauty"]
    if "finland" in query.lower():
        payload["filter"].setdefault("audience", {})["location"] = [{"id": "FI", "weight": 0.3}]
    if "sweden" in query.lower():
        payload["filter"].setdefault("audience", {})["location"] = [{"id": "SE", "weight": 0.3}]
    if "fitness" in query.lower():
        payload["filter"]["influencer"]["topics"] = ["fitness"]

    return payload

@app.post("/modash")
async def search_all_platforms(request: Request):
    body = await request.json()
    query = body.get("query", "")

    results = []

    for platform, url in PLATFORM_ENDPOINTS.items():
        payload = create_payload(query)
        try:
            response = requests.post(url, headers=HEADERS, json=payload)
            response.raise_for_status()
            data = response.json()
            for influencer in data.get("data", [])[:3]:  # limit results from each platform
                influencer["platform"] = platform
                results.append(influencer)
        except Exception as e:
            results.append({"platform": platform, "error": str(e)})

    return {"influencers": results[:10]}
