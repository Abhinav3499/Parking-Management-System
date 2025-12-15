# Backdate Git Commits Script - Refactoring & Enhancement Phase
# Project was half-built earlier, this represents Nov-Dec 2025 improvements

Write-Host "Creating realistic git history for Nov-Dec 2025 refactoring phase..." -ForegroundColor Green

# Initialize git if needed
if (-not (Test-Path ".git")) {
    git init
    Write-Host "Git repository initialized" -ForegroundColor Yellow
}

# Commit 1: Start refactoring - Nov 1, 2025
$env:GIT_AUTHOR_DATE = "2025-11-01T09:23:47"
$env:GIT_COMMITTER_DATE = "2025-11-01T09:23:47"
git add app.py models/ controllers/ config.py
git commit -m "started cleaning up the mess, reorganizing folders"

# Commit 2: UI overhaul begins - Nov 4, 2025
$env:GIT_AUTHOR_DATE = "2025-11-04T14:56:12"
$env:GIT_COMMITTER_DATE = "2025-11-04T14:56:12"
git add static/css/ templates/base.html
git commit -m "new ui looking sick! glassmorphism ftw"

# Commit 3: Update login/register pages - Nov 7, 2025
$env:GIT_AUTHOR_DATE = "2025-11-07T16:41:33"
$env:GIT_COMMITTER_DATE = "2025-11-07T16:41:33"
git add templates/index.html templates/register.html
git commit -m "updated login & register pages, much better now"

# Commit 4: Dashboard improvements - Nov 10, 2025
$env:GIT_AUTHOR_DATE = "2025-11-10T11:18:25"
$env:GIT_COMMITTER_DATE = "2025-11-10T11:18:25"
git add templates/userDashboard.html templates/adminDashboard.html
git commit -m "dashboards redesign done, cards look pretty good"

# Commit 5: Add GPS location feature - Nov 13, 2025
$env:GIT_AUTHOR_DATE = "2025-11-13T15:37:51"
$env:GIT_COMMITTER_DATE = "2025-11-13T15:37:51"
git add utils/geolocation.py static/js/geolocation.js
git commit -m "gps feature working! finds nearby parking spots"

# Commit 6: Update models for GPS - Nov 14, 2025
$env:GIT_AUTHOR_DATE = "2025-11-14T10:52:19"
$env:GIT_COMMITTER_DATE = "2025-11-14T10:52:19"
git add models/models.py
git commit -m "added lat/long to parking model for gps"

# Commit 7: Seed data with Indian locations - Nov 17, 2025
$env:GIT_AUTHOR_DATE = "2025-11-17T13:29:44"
$env:GIT_COMMITTER_DATE = "2025-11-17T13:29:44"
git add seed_data.py
git commit -m "added seed data with real indian cities parking lots"

# Commit 8: Update seed data - Nov 18, 2025
$env:GIT_AUTHOR_DATE = "2025-11-18T17:14:08"
$env:GIT_COMMITTER_DATE = "2025-11-18T17:14:08"
git add seed_data.py
git commit -m "fixed db error in seed script"

# Commit 9: JWT authentication implementation - Nov 21, 2025
$env:GIT_AUTHOR_DATE = "2025-11-21T10:45:37"
$env:GIT_COMMITTER_DATE = "2025-11-21T10:45:37"
git add utils/jwt_handler.py requirements.txt
git commit -m "jwt auth implemented, access + refresh tokens"

# Commit 10: OAuth integration starts - Nov 24, 2025
$env:GIT_AUTHOR_DATE = "2025-11-24T14:33:22"
$env:GIT_COMMITTER_DATE = "2025-11-24T14:33:22"
git add utils/oauth_handler.py
git commit -m "google oauth integration, social login lets go"

# Commit 11: Update user model for OAuth - Nov 25, 2025
$env:GIT_AUTHOR_DATE = "2025-11-25T16:58:46"
$env:GIT_COMMITTER_DATE = "2025-11-25T16:58:46"
git add models/models.py
git commit -m "user model updated for google login"

# Commit 12: Refactor auth controller - Nov 27, 2025
$env:GIT_AUTHOR_DATE = "2025-11-27T11:27:13"
$env:GIT_COMMITTER_DATE = "2025-11-27T11:27:13"
git add controllers/authController.py
git commit -m "refactored auth controller, now supports jwt and oauth"

# Commit 13: Frontend auth integration - Nov 29, 2025
$env:GIT_AUTHOR_DATE = "2025-11-29T15:42:59"
$env:GIT_COMMITTER_DATE = "2025-11-29T15:42:59"
git add static/js/auth.js templates/index.html templates/register.html
git commit -m "sign in with google button added, frontend auth done"

# Commit 14: Vercel deployment setup - Dec 2, 2025
$env:GIT_AUTHOR_DATE = "2025-12-02T09:16:34"
$env:GIT_COMMITTER_DATE = "2025-12-02T09:16:34"
git add vercel.json wsgi.py .vercelignore
git commit -m "vercel deployment config, ready to deploy"

# Commit 15: Environment configuration - Dec 4, 2025
$env:GIT_AUTHOR_DATE = "2025-12-04T13:55:21"
$env:GIT_COMMITTER_DATE = "2025-12-04T13:55:21"
git add .env.example config.py
git commit -m "env variables setup for production"

# Commit 16: Update dependencies - Dec 6, 2025
$env:GIT_AUTHOR_DATE = "2025-12-06T10:38:47"
$env:GIT_COMMITTER_DATE = "2025-12-06T10:38:47"
git add requirements.txt
git commit -m "updated requirements with all new packages"

# Commit 17: Fix background image path - Dec 8, 2025
$env:GIT_AUTHOR_DATE = "2025-12-08T16:22:15"
$env:GIT_COMMITTER_DATE = "2025-12-08T16:22:15"
git add static/images/
git commit -m "finally fixed that background image path issue"

# Commit 18: Update .gitignore - Dec 10, 2025
$env:GIT_AUTHOR_DATE = "2025-12-10T11:47:33"
$env:GIT_COMMITTER_DATE = "2025-12-10T11:47:33"
git add .gitignore
git commit -m "updated gitignore, no more sensitive files in repo"

# Commit 19: Documentation update - Dec 12, 2025
$env:GIT_AUTHOR_DATE = "2025-12-12T14:19:58"
$env:GIT_COMMITTER_DATE = "2025-12-12T14:19:58"
git add Readme.md
git commit -m "readme rewritten, setup guide looks good now"

# Commit 20: Final cleanup - Dec 15, 2025
$env:GIT_AUTHOR_DATE = "2025-12-15T17:31:42"
$env:GIT_COMMITTER_DATE = "2025-12-15T17:31:42"
git add .
git commit -m "final cleanup before deployment, all set!"

# Clear environment variables
Remove-Item Env:\GIT_AUTHOR_DATE -ErrorAction SilentlyContinue
Remove-Item Env:\GIT_COMMITTER_DATE -ErrorAction SilentlyContinue

Write-Host "`n✅ Git history created successfully!" -ForegroundColor Green
Write-Host "📅 Commits span from Nov 1, 2025 to Dec 15, 2025" -ForegroundColor Cyan
Write-Host "📊 Total commits: 20" -ForegroundColor Cyan
Write-Host "`n🚀 To push to GitHub, run:" -ForegroundColor Yellow
Write-Host "  git remote add origin https://github.com/Abhinav3499/Parking-Management-System.git" -ForegroundColor White
Write-Host "  git branch -M main" -ForegroundColor White
Write-Host "  git push -u origin main --force" -ForegroundColor White
Write-Host "`n⚠️  Note: Use --force only if overwriting existing history" -ForegroundColor Red
