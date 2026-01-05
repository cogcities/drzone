#!/usr/bin/env python3
"""
DrZo Ecosystem Query Script
Queries GitHub GraphQL API to collect ecosystem data including:
- Organizations
- Repositories
- Users (followers/following)
- Teams and memberships
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
GITHUB_REST_URL = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN")
ECOSYSTEM_USER = os.environ.get("ECOSYSTEM_USER", "drzo")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def graphql_query(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query against GitHub API."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(GITHUB_GRAPHQL_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def rest_query(endpoint: str, params: dict = None) -> dict:
    """Execute a REST API query against GitHub API."""
    url = f"{GITHUB_REST_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def get_user_info() -> dict:
    """Get authenticated user information."""
    query = """
    query {
      viewer {
        login
        id
        name
        bio
        company
        location
        email
        websiteUrl
        avatarUrl
        createdAt
        updatedAt
        followers { totalCount }
        following { totalCount }
        repositories { totalCount }
        starredRepositories { totalCount }
        organizations { totalCount }
        gists { totalCount }
      }
    }
    """
    result = graphql_query(query)
    return result.get("data", {}).get("viewer", {})


def get_organizations(user: str = None) -> list:
    """Get all organizations for the user."""
    orgs = []
    cursor = None
    
    while True:
        query = """
        query($cursor: String) {
          viewer {
            organizations(first: 100, after: $cursor) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                login
                id
                name
                description
                url
                avatarUrl
                createdAt
                membersWithRole { totalCount }
                repositories { totalCount }
                teams { totalCount }
              }
            }
          }
        }
        """
        result = graphql_query(query, {"cursor": cursor})
        data = result.get("data", {}).get("viewer", {}).get("organizations", {})
        
        orgs.extend(data.get("nodes", []))
        
        if not data.get("pageInfo", {}).get("hasNextPage"):
            break
        cursor = data["pageInfo"]["endCursor"]
    
    return orgs


def get_repositories(limit: int = 1000) -> list:
    """Get repositories accessible to the user."""
    repos = []
    cursor = None
    
    while len(repos) < limit:
        query = """
        query($cursor: String) {
          viewer {
            repositories(first: 100, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                nameWithOwner
                name
                description
                url
                isPrivate
                isFork
                isArchived
                createdAt
                updatedAt
                pushedAt
                primaryLanguage { name }
                stargazerCount
                forkCount
                issues { totalCount }
                pullRequests { totalCount }
                defaultBranchRef { name }
                owner {
                  login
                  ... on Organization { id }
                  ... on User { id }
                }
              }
            }
          }
        }
        """
        result = graphql_query(query, {"cursor": cursor})
        data = result.get("data", {}).get("viewer", {}).get("repositories", {})
        
        repos.extend(data.get("nodes", []))
        
        if not data.get("pageInfo", {}).get("hasNextPage"):
            break
        cursor = data["pageInfo"]["endCursor"]
    
    return repos[:limit]


def get_followers() -> list:
    """Get user's followers."""
    followers = []
    cursor = None
    
    while True:
        query = """
        query($cursor: String) {
          viewer {
            followers(first: 100, after: $cursor) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                login
                id
                name
                avatarUrl
                bio
                company
                location
                followers { totalCount }
                following { totalCount }
                repositories { totalCount }
              }
            }
          }
        }
        """
        result = graphql_query(query, {"cursor": cursor})
        data = result.get("data", {}).get("viewer", {}).get("followers", {})
        
        followers.extend(data.get("nodes", []))
        
        if not data.get("pageInfo", {}).get("hasNextPage"):
            break
        cursor = data["pageInfo"]["endCursor"]
    
    return followers


def get_following() -> list:
    """Get users the authenticated user is following."""
    following = []
    cursor = None
    
    while True:
        query = """
        query($cursor: String) {
          viewer {
            following(first: 100, after: $cursor) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                login
                id
                name
                avatarUrl
                bio
                company
                location
                followers { totalCount }
                following { totalCount }
                repositories { totalCount }
              }
            }
          }
        }
        """
        result = graphql_query(query, {"cursor": cursor})
        data = result.get("data", {}).get("viewer", {}).get("following", {})
        
        following.extend(data.get("nodes", []))
        
        if not data.get("pageInfo", {}).get("hasNextPage"):
            break
        cursor = data["pageInfo"]["endCursor"]
    
    return following


def get_starred_repos(limit: int = 500) -> list:
    """Get starred repositories."""
    starred = []
    cursor = None
    
    while len(starred) < limit:
        query = """
        query($cursor: String) {
          viewer {
            starredRepositories(first: 100, after: $cursor, orderBy: {field: STARRED_AT, direction: DESC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                nameWithOwner
                name
                description
                url
                stargazerCount
                forkCount
                primaryLanguage { name }
              }
            }
          }
        }
        """
        result = graphql_query(query, {"cursor": cursor})
        data = result.get("data", {}).get("viewer", {}).get("starredRepositories", {})
        
        starred.extend(data.get("nodes", []))
        
        if not data.get("pageInfo", {}).get("hasNextPage"):
            break
        cursor = data["pageInfo"]["endCursor"]
    
    return starred[:limit]


def get_gists() -> list:
    """Get user's gists."""
    gists = []
    cursor = None
    
    while True:
        query = """
        query($cursor: String) {
          viewer {
            gists(first: 100, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                name
                description
                url
                isPublic
                createdAt
                updatedAt
                files { name }
              }
            }
          }
        }
        """
        result = graphql_query(query, {"cursor": cursor})
        data = result.get("data", {}).get("viewer", {}).get("gists", {})
        
        gists.extend(data.get("nodes", []))
        
        if not data.get("pageInfo", {}).get("hasNextPage"):
            break
        cursor = data["pageInfo"]["endCursor"]
    
    return gists


def save_data(filename: str, data: any):
    """Save data to JSON file."""
    filepath = DATA_DIR / filename
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Saved {filepath}")


def main():
    """Main function to query and save ecosystem data."""
    print("=" * 60)
    print("DrZo Ecosystem Query")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    if not TOKEN:
        print("ERROR: GITHUB_TOKEN environment variable not set")
        exit(1)
    
    # Query all data
    print("\n[1/7] Querying user info...")
    user_info = get_user_info()
    save_data("user_info.json", user_info)
    print(f"  User: {user_info.get('login')}")
    
    print("\n[2/7] Querying organizations...")
    orgs = get_organizations()
    save_data("organizations.json", orgs)
    print(f"  Found {len(orgs)} organizations")
    
    print("\n[3/7] Querying repositories (up to 1000)...")
    repos = get_repositories(limit=1000)
    save_data("repositories.json", repos)
    print(f"  Found {len(repos)} repositories")
    
    print("\n[4/7] Querying followers...")
    followers = get_followers()
    save_data("followers.json", followers)
    print(f"  Found {len(followers)} followers")
    
    print("\n[5/7] Querying following...")
    following = get_following()
    save_data("following.json", following)
    print(f"  Found {len(following)} following")
    
    print("\n[6/7] Querying starred repositories...")
    starred = get_starred_repos()
    save_data("starred_repos.json", starred)
    print(f"  Found {len(starred)} starred repos")
    
    print("\n[7/7] Querying gists...")
    gists = get_gists()
    save_data("gists.json", gists)
    print(f"  Found {len(gists)} gists")
    
    # Save summary
    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user_info.get("login"),
        "counts": {
            "organizations": len(orgs),
            "repositories": len(repos),
            "followers": len(followers),
            "following": len(following),
            "starred_repos": len(starred),
            "gists": len(gists),
        }
    }
    save_data("summary.json", summary)
    
    print("\n" + "=" * 60)
    print("Ecosystem query complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
