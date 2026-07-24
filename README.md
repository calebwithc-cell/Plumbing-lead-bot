# Mrs. Gordon's & Plumbing — Lead Checker

Checks Craigslist (Hudson Valley / Rockland County) every 20 minutes for
plumbing-related posts and sends a phone notification via ntfy.sh when it
finds a new one. 100% free to run.

**What it does NOT do:** pull from Thumbtack, Angi, HomeAdvisor, Yelp, or
Facebook. Those sites block automated access in their terms of service, so
this only uses Craigslist's public RSS feeds, which are fine to poll.

## One-time setup (about 10 minutes)

### 1. Install ntfy on the phone that should get alerts
- iOS: search "ntfy" on the App Store
- Android: search "ntfy" on Google Play
- Open the app, tap **+**, and subscribe to this exact topic:
  ```
  mrs-gordons-plumbing-7x9k
  ```
- That topic name is your "channel" — anyone who knows it can send to it,
  so don't post it publicly. If you want to change it, edit `NTFY_TOPIC`
  in `check_leads.py` and re-subscribe in the app to match.

### 2. Put this code in a GitHub repo
- Create a free GitHub account if you don't have one: https://github.com/join
- Create a new repository (e.g. `plumbing-lead-bot`)
- Upload these files, keeping the folder structure:
  ```
  check_leads.py
  seen_posts.json      (create as an empty file with just: [])
  .github/workflows/check-leads.yml
  ```

### 3. Turn on Actions
- In the repo, go to the **Actions** tab and enable workflows if prompted
- The workflow runs automatically every 20 minutes once it's in the repo
- To test it immediately: go to **Actions → Check Plumbing Leads → Run workflow**

That's it — no server, no hosting, no monthly cost.

## Customizing

- **Keywords**: edit the `KEYWORDS` list in `check_leads.py`
- **How often it checks**: edit the cron schedule in
  `.github/workflows/check-leads.yml` (default is every 20 min; GitHub's
  minimum practical interval is about 5 min, though it can lag under load)
- **Area**: currently set to Rockland County via `hudsonvalley.craigslist.org`.
  If leads should also come from a neighboring metro (e.g. Bergen County,
  NJ or Westchester), a second set of feed URLs can be added for that
  region too — just ask and I can add it.

## A few honest limitations

- Craigslist lead volume for skilled-trade gigs varies a lot by area — it
  may be quiet some weeks and busier others.
- Duplicate detection is based on Craigslist's post ID, so reposts of the
  same ad won't re-alert.
- This is not a replacement for paid lead platforms if most of the
  business currently comes from there — it's a free supplemental source.
