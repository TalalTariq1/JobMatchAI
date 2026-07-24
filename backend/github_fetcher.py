import os
import json
import requests
from dotenv import load_dotenv
from groq import Groq



def fetch_github_repos(username):
    """Fetch a user's public GitHub repositories."""
    response = requests.get(f"https://api.github.com/users/{username}/repos")
    repos = response.json()
    return [
        {
            "name": repo["name"],
            "description": repo.get("description"),
            "primary_language": repo.get("language"),
            "stars": repo.get("stargazers_count"),
        }
        for repo in repos
    ]


def summarize_github_profile(repos):
    """Summarize a GitHub profile from repository data."""
    load_dotenv()
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    prompt = f"""Carefully review EVERY SINGLE repository listed below, one by one. Do not
    skip any repo or assume it's unimportant just because its description is short or its
    star count is low — a repo with 0 stars can still be a genuinely relevant project
    (e.g. a notes app, a small utility, a personal tool), and must not be excluded.

    Return a JSON object with:
    - top_languages: list of 3-5 languages this person uses most, based on ALL repos
    - project_themes: list of 3-5 short phrases describing the range of projects they build,
      based on ALL repos, not just the highest-starred ones
    - notable_projects: a list with ONE entry for EVERY repository provided below (do not omit
      any, do not cap the list length), each with:
        - repo_name: the exact repo name
        - description: a one-sentence plain-English description of what it does, inferred
          from its name/description/language if the original description is missing or vague
        - reason: a short note on what kind of role/skill this repo could be relevant
          evidence for (e.g. "frontend/UI work", "personal productivity tooling",
          "API integration practice") — every repo gets a note, even small/simple ones

    Repositories ({len(repos)} total — your notable_projects list MUST contain exactly {len(repos)} entries):
    {json.dumps(repos, indent=2)}
    """
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    repos = fetch_github_repos("torvalds")
    summary = summarize_github_profile(repos)
    print(summary)