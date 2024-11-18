"""
Service script to clean up caches that were not deleted by
the app itself, e.g. due to an error.
Not crucial thanks to auto-deletion timeouts, but could
save money with a paid API tier.
"""

from pathlib import Path

import google.generativeai as genai

from before_you_sign.config import load_config


def main():
    project_root = Path(__file__).parents[2]
    config = load_config(project_root / "local/config.yaml")
    api_key = config["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    caches = list(genai.caching.CachedContent.list())
    if not caches:
        print("No caches")
        return
    for cache in caches:
        cache.delete()
    print(f"Deleted {len(caches)}")


if __name__ == "__main__":
    main()
