# DrZone - Ecosystem Dashboard

> Automated ecosystem tracking for the drzo GitHub network

**Status:** 🔄 Awaiting first update

## 📊 Overview

This repository automatically tracks and documents the drzo GitHub ecosystem, including:

- **Organizations** - All organizations the user is a member of
- **Repositories** - Repository listings across all organizations
- **Users** - Followers and following relationships
- **Activity** - Starred repos, gists, and more

## 🔄 Update Schedule

This dashboard is automatically updated every **Sunday at 00:00 UTC** via GitHub Actions.

You can also trigger a manual update from the [Actions tab](../../actions/workflows/update-ecosystem.yml).

## 📁 Data Files

Once the first update runs, the following data files will be available:

- `data/summary.json` - Overview statistics
- `data/organizations.json` - Organization details
- `data/repositories.json` - Repository listings
- `data/followers.json` - Follower information
- `data/following.json` - Following information
- `data/starred_repos.json` - Starred repositories
- `data/gists.json` - Gist information

## 🛠️ Configuration

The workflow uses the `ECOSYSTEM_PAT` secret to authenticate with the GitHub GraphQL API.

### Required Permissions

The PAT should have the following scopes:
- `read:org` - Read organization data
- `read:user` - Read user profile data
- `repo` - Read repository data (for private repos)

## 🚀 Manual Trigger

To manually trigger an update:

1. Go to the [Actions tab](../../actions)
2. Select "Update DrZo Ecosystem Listings"
3. Click "Run workflow"
4. Optionally enable "Perform full ecosystem scan"
5. Click "Run workflow"

---

*Powered by [Git PAT Beast](https://github.com/cogcities/drzone) 🦁*
