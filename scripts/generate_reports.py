#!/usr/bin/env python3
"""
DrZo Ecosystem Report Generator
Generates Markdown reports from the collected ecosystem data.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("data")


def load_json(filename: str) -> any:
    """Load JSON data from file."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return None
    with open(filepath) as f:
        return json.load(f)


def generate_readme():
    """Generate the main README.md with ecosystem overview."""
    summary = load_json("summary.json")
    user_info = load_json("user_info.json")
    enterprises = load_json("enterprises.json") or []
    orgs = load_json("organizations.json") or []
    repos = load_json("repositories.json") or []
    
    if not summary:
        print("No summary data found, skipping README generation")
        return
    
    # Categorize organizations
    org_categories = categorize_organizations(orgs)
    
    # Analyze repositories
    repo_stats = analyze_repositories(repos)
    
    # Map organizations to enterprises
    enterprise_org_map = map_orgs_to_enterprises(enterprises)
    
    # Generate README content
    content = f"""# DrZone - Ecosystem Dashboard

> Automated ecosystem tracking for the drzo GitHub network

**Last Updated:** {summary.get('timestamp', 'Unknown')}

## 📊 Overview

| Metric | Count |
|--------|-------|
| Enterprises | {summary['counts'].get('enterprises', 0)} |
| Organizations | {summary['counts']['organizations']} |
| Repositories | {summary['counts']['repositories']} |
| Followers | {summary['counts']['followers']} |
| Following | {summary['counts']['following']} |
| Starred Repos | {summary['counts']['starred_repos']} |
| Gists | {summary['counts']['gists']} |

## 🏛️ Enterprises

"""
    
    if enterprises:
        content += "| Enterprise | Slug | Organizations | Members | Admin |\n"
        content += "|------------|------|---------------|---------|-------|\n"
        for ent in enterprises:
            name = ent.get('name', 'Unknown')
            slug = ent.get('slug', '')
            url = ent.get('url', f'https://github.com/enterprises/{slug}')
            org_count = ent.get('organizations', {}).get('totalCount', 0)
            member_count = ent.get('members', {}).get('totalCount', 0)
            is_admin = "✅" if ent.get('viewerIsAdmin') else "❌"
            content += f"| [{name}]({url}) | `{slug}` | {org_count} | {member_count} | {is_admin} |\n"
        
        content += "\n### Enterprise → Organization Mapping\n\n"
        for ent in enterprises:
            ent_name = ent.get('name', 'Unknown')
            ent_slug = ent.get('slug', '')
            ent_orgs = ent.get('organizations', {}).get('nodes', [])
            if ent_orgs:
                content += f"#### {ent_name} (`{ent_slug}`)\n\n"
                content += "| Organization | Repos | Members | Description |\n"
                content += "|--------------|-------|---------|-------------|\n"
                for org in sorted(ent_orgs, key=lambda x: x.get('repositories', {}).get('totalCount', 0), reverse=True):
                    login = org.get('login', 'Unknown')
                    repo_count = org.get('repositories', {}).get('totalCount', 0)
                    member_count = org.get('membersWithRole', {}).get('totalCount', 0)
                    desc = (org.get('description') or 'No description')[:40]
                    content += f"| [{login}](https://github.com/{login}) | {repo_count} | {member_count} | {desc} |\n"
                content += "\n"
    else:
        content += "*No enterprise data available*\n\n"
    
    content += """## 🏢 Organization Categories

"""
    
    for category, org_list in org_categories.items():
        if org_list:
            content += f"### {category}\n\n"
            content += "| Organization | Repos | Members | Description |\n"
            content += "|--------------|-------|---------|-------------|\n"
            for org in sorted(org_list, key=lambda x: x.get('repositories', {}).get('totalCount', 0), reverse=True)[:10]:
                name = org.get('login', 'Unknown')
                repo_count = org.get('repositories', {}).get('totalCount', 0)
                member_count = org.get('membersWithRole', {}).get('totalCount', 0)
                desc = (org.get('description') or 'No description')[:50]
                content += f"| [{name}](https://github.com/{name}) | {repo_count} | {member_count} | {desc} |\n"
            content += "\n"
    
    content += f"""## 💻 Repository Statistics

| Metric | Value |
|--------|-------|
| Total Repositories | {len(repos)} |
| Public | {repo_stats['public']} |
| Private | {repo_stats['private']} |
| Forks | {repo_stats['forks']} |
| Original | {repo_stats['original']} |
| Archived | {repo_stats['archived']} |

### Top Languages

| Language | Count | Percentage |
|----------|-------|------------|
"""
    
    total_with_lang = sum(repo_stats['languages'].values())
    for lang, count in sorted(repo_stats['languages'].items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = (count / total_with_lang * 100) if total_with_lang > 0 else 0
        content += f"| {lang} | {count} | {pct:.1f}% |\n"
    
    content += f"""
### Recently Updated Repositories

| Repository | Language | Stars | Updated |
|------------|----------|-------|---------|
"""
    
    for repo in repos[:15]:
        name = repo.get('nameWithOwner', 'Unknown')
        lang = repo.get('primaryLanguage', {})
        lang_name = lang.get('name', 'Unknown') if lang else 'Unknown'
        stars = repo.get('stargazerCount', 0)
        updated = repo.get('updatedAt', '')[:10]
        content += f"| [{name}](https://github.com/{name}) | {lang_name} | {stars} | {updated} |\n"
    
    content += """
## 📁 Data Files

The following data files are automatically updated:

- [`data/summary.json`](data/summary.json) - Overview statistics
- [`data/enterprises.json`](data/enterprises.json) - Enterprise details
- [`data/organizations.json`](data/organizations.json) - Organization details
- [`data/repositories.json`](data/repositories.json) - Repository listings
- [`data/followers.json`](data/followers.json) - Follower information
- [`data/following.json`](data/following.json) - Following information
- [`data/starred_repos.json`](data/starred_repos.json) - Starred repositories
- [`data/gists.json`](data/gists.json) - Gist information

## 🔄 Update Schedule

This dashboard is automatically updated every **Sunday at 00:00 UTC** via GitHub Actions.

You can also trigger a manual update from the [Actions tab](../../actions/workflows/update-ecosystem.yml).

---

*Generated by [DrZone Ecosystem Tracker](https://github.com/cogcities/drzone)*
"""
    
    with open("README.md", "w") as f:
        f.write(content)
    
    print("Generated README.md")


def map_orgs_to_enterprises(enterprises: list) -> dict:
    """Create a mapping of organization logins to their parent enterprise."""
    mapping = {}
    for ent in enterprises:
        ent_name = ent.get('name', 'Unknown')
        ent_slug = ent.get('slug', '')
        for org in ent.get('organizations', {}).get('nodes', []):
            mapping[org.get('login')] = {
                'enterprise_name': ent_name,
                'enterprise_slug': ent_slug
            }
    return mapping


def categorize_organizations(orgs: list) -> dict:
    """Categorize organizations by type."""
    categories = {
        'Core Cognitive': [],
        'Zone Network': [],
        'RegimA Network': [],
        'O9 Network': [],
        'Echo Mirrors': [],
        'Special Purpose': [],
        'Other': []
    }
    
    for org in orgs:
        login = org.get('login', '').lower()
        
        if any(x in login for x in ['cog', 'oz', 'echo']):
            categories['Core Cognitive'].append(org)
        elif any(x in login for x in ['zone', 'rez', 'rzone']):
            categories['Zone Network'].append(org)
        elif 'regima' in login:
            categories['RegimA Network'].append(org)
        elif login.startswith('o9') or login.startswith('o6') or 'e9' in login:
            categories['O9 Network'].append(org)
        elif 'org-echo' in login:
            categories['Echo Mirrors'].append(org)
        elif any(x in login for x in ['unicorn', 'cosmic', 'kaw', 'hyper', 'marduk', 'gnn']):
            categories['Special Purpose'].append(org)
        else:
            categories['Other'].append(org)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def analyze_repositories(repos: list) -> dict:
    """Analyze repository statistics."""
    stats = {
        'public': 0,
        'private': 0,
        'forks': 0,
        'original': 0,
        'archived': 0,
        'languages': defaultdict(int),
        'by_owner': defaultdict(int)
    }
    
    for repo in repos:
        if repo.get('isPrivate'):
            stats['private'] += 1
        else:
            stats['public'] += 1
        
        if repo.get('isFork'):
            stats['forks'] += 1
        else:
            stats['original'] += 1
        
        if repo.get('isArchived'):
            stats['archived'] += 1
        
        lang = repo.get('primaryLanguage')
        if lang:
            stats['languages'][lang.get('name', 'Unknown')] += 1
        
        owner = repo.get('owner', {}).get('login', 'Unknown')
        stats['by_owner'][owner] += 1
    
    return stats


def main():
    """Main function to generate reports."""
    print("=" * 60)
    print("DrZo Ecosystem Report Generator")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    generate_readme()
    
    print("\n" + "=" * 60)
    print("Report generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
