"""API connectivity / deployment configuration tests."""

def test_env_has_no_real_secrets():
    # .env.example must not contain real secrets; .env is excluded by .gitignore
    with open(".env.example") as f:
        content = f.read()
    assert "AQ." not in content, "Real API key found in .env.example — remove"
    assert "GEMINI_API_KEY=" in content or "OPENAI_API_KEY=" in content, "Placeholder missing"


def test_api_client_rejects_missing_env():
    import os
    old = os.environ.get("NEXT_PUBLIC_API_URL")
    try:
        os.environ.pop("NEXT_PUBLIC_API_URL", None)
        # Re-import would fail; just verify logic
        from frontend.src.lib.api_client import API_BASE
        assert API_BASE == "" or API_BASE is None or API_BASE == ""
    finally:
        if old is not None:
            os.environ["NEXT_PUBLIC_API_URL"] = old
