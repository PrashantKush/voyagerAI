import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client as create_supabase_client

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Supabase – strip whitespace so .env typos don't break
supabase_url = (os.getenv("SUPABASE_URL") or "").strip()
supabase_key = (os.getenv("SUPABASE_KEY") or "").strip()
supabase = None
if supabase_url and supabase_key:
    supabase = create_supabase_client(supabase_url, supabase_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ask-ai")
async def ask_ai(
    prompt: str,
    user_name: str | None = Query(None, description="User's name"),
    user_email: str | None = Query(None, description="User's email"),
):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a travel expert at MakeMyTrip. Provide concise, expert travel advice."},
                {"role": "user", "content": prompt}
            ],
        )
        answer = response.choices[0].message.content

        # Log to Supabase if configured and we have at least one user detail
        log_error = None
        if supabase and (user_name or user_email):
            try:
                supabase.table("trip_logs").insert({
                    "user_name": user_name or None,
                    "user_email": user_email or None,
                    "query": prompt,
                    "response": answer,
                }).execute()
            except Exception as log_err:
                log_error = str(log_err)
                print(f"Supabase log error: {log_error}")
        elif not supabase and (user_name or user_email):
            log_error = "Supabase not configured (missing SUPABASE_URL or SUPABASE_KEY)"

        out = {"answer": answer}
        if log_error:
            out["log_error"] = log_error
        return out
    except Exception as e:
        return {"answer": f"Error calling AI: {str(e)}"}

@app.get("/")
def home():
    return {"status": "AI Backend is Live"}


@app.get("/log-test")
async def log_test():
    """Insert a test row into trip_logs. Use to verify Supabase connection and RLS."""
    if not supabase:
        return {
            "ok": False,
            "error": "Supabase not configured",
            "hint": "Set SUPABASE_URL and SUPABASE_KEY in Render env vars (no spaces around =).",
        }
    try:
        supabase.table("trip_logs").insert({
            "user_name": "Test User",
            "user_email": "test@example.com",
            "query": "Test query from /log-test",
            "response": "Test response entry.",
        }).execute()
        return {"ok": True, "message": "Test entry inserted. Check Supabase Table Editor → trip_logs."}
    except Exception as e:
        return {"ok": False, "error": str(e)}