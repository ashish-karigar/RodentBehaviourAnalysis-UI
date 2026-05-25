# RodentBehaviourAnalysis UI

A modern PyQt6 desktop client for securely logging into the RodentBehaviourAnalysis system, uploading rodent maze videos to the backend, monitoring processing jobs, and downloading processed result packages.

The UI is designed as a lightweight desktop application for macOS and Windows. It connects to a hosted or local FastAPI backend that runs the actual ML pipeline using DeepLabCut, YOLOv8 maze/zone detection, Redis queueing, and SQLite job tracking.

---

## Abstract

Rodent behavior analysis workflows often involve large raw videos, heavy ML processing, and multiple generated outputs such as cropped videos, tracking files, segment clips, metadata sheets, and Excel reports. Running the full ML pipeline directly from a user-facing desktop app can overload machines and make the setup difficult for end users.

This UI separates the user-facing experience from the ML workload. Users authenticate through Firebase, select a folder of raw videos, add selected videos to a backend queue, monitor each job through reusable status cards, and download ZIP result packages after processing. The backend handles the actual processing sequentially so the ML system is not overloaded.

---

## Introduction

The goal of this desktop UI is to make the RodentBehaviourAnalysis pipeline easier to use for researchers, lab staff, and technical users who need a clean interface instead of terminal commands.

Current UI workflow:

1. User opens the app.
2. User logs in using Firebase Authentication.
3. App checks the user profile in Firestore.
4. If `mustChangePassword` is true, the user is asked to update their password before entering the app.
5. User enters the main app.
6. User browses a folder containing raw rodent maze videos.
7. Supported videos are listed with checkboxes.
8. User adds selected videos to the backend queue.
9. Each uploaded video appears as a reusable job card.
10. User monitors queued, processing, completed, downloaded, expired, or failed jobs.
11. User downloads completed ZIP outputs.

The current version focuses on the **Process** tab. The **Visualize** tab is planned for reviewing processed segment videos and generated spreadsheet outputs.

---

## Current Status

Implemented:

- PyQt6 desktop UI
- Firebase email/password login
- Firestore-backed user profile check
- Admin-controlled access model
- No public signup flow
- First-login password change flow using Firestore `mustChangePassword`
- Forgot password flow using Firebase reset email
- Light/dark theme support
- Theme icon using local image assets
- Logout icon using local image asset
- Folder-based video discovery
- Checkbox-based video selection
- Add-to-queue behavior for multiple videos
- Ability to add more videos while existing jobs are processing
- Reusable job cards for each uploaded video
- Status polling from backend
- Backend upload integration
- Result ZIP download
- Default download location set to the user's Downloads folder
- Download button states:
  - queued/expired: disabled muted button
  - processing: disabled warning button
  - completed: active green download button
  - downloaded: disabled button with green outline

Backend expected:

- FastAPI server running at `http://127.0.0.1:8000`
- Redis/RQ worker running
- Cleanup worker running
- Backend endpoints:
  - `GET /health`
  - `POST /jobs/upload-video`
  - `GET /jobs/{job_id}/status`
  - `GET /jobs/{job_id}/download`

---

## Planned Features

Upcoming:

- Protect backend API with Firebase ID token verification
- Send Firebase ID token with backend upload/status/download requests
- User-specific job visibility on backend
- Backend job cancellation endpoint
- True cancel/stop support for already-submitted backend jobs
- Better job history screen
- Visualize tab for reviewing processed outputs
- Packaged installers for macOS and Windows
- Configurable backend URL from UI settings
- Improved progress reporting from backend if available
- Better error recovery for expired/downloaded jobs
- Optional admin dashboard for managing users and password-change flags

---

## Project Structure

```text
RodentBehaviourAnalysis-UI/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ assets/
│  ├─ moon.png
│  ├─ sun.png
│  └─ people-4.png
└─ src/
   ├─ main.py
   ├─ api_client.py
   ├─ config.py
   ├─ auth/
   │  ├─ __init__.py
   │  ├─ auth_state.py
   │  ├─ firebase_auth.py
   │  └─ firestore_user.py
   └─ ui/
      ├─ app_window.py
      ├─ login_window.py
      ├─ theme.py
      ├─ main_window.py              # older prototype; can be removed later
      ├─ pages/
      │  ├─ process_page.py
      │  └─ visualize_page.py
      └─ components/
         ├─ app_button.py
         ├─ job_card.py
         ├─ status_badge.py
         └─ video_list_item.py
```

---

## Key Entry Points

- `src/main.py`  
  Starts the PyQt6 app, validates environment config, opens the login screen first, and then opens the main app after successful authentication.

- `src/ui/login_window.py`  
  Login screen, password visibility toggle, Firebase sign-in, forgot password, and first-login password change UI.

- `src/ui/app_window.py`  
  Main app shell with top bar, theme toggle, logout button, and tabs.

- `src/ui/pages/process_page.py`  
  Main processing workflow: browse folder, select videos, add to queue, monitor jobs, and download results.

- `src/ui/components/job_card.py`  
  Reusable processing queue card for each uploaded video.

- `src/ui/theme.py`  
  Centralized light/dark theme and shared stylesheet.

- `src/auth/firebase_auth.py`  
  Firebase Auth REST functions for login, password reset, and password update.

- `src/auth/firestore_user.py`  
  Firestore REST functions for reading/updating user profile flags.

- `src/auth/auth_state.py`  
  Stores the current authenticated user's token and identity data in memory.

- `src/api_client.py`  
  Handles HTTP communication with the RodentBehaviourAnalysis backend API.

- `src/config.py`  
  Loads environment variables and app-level config.

---

## Fresh Setup Guide

### 1) Clone the repository

```bash
git clone <repository-url>
cd RodentBehaviourAnalysis-UI
```

### 2) Create and activate Python environment

Recommended:

```bash
conda create -n RBA-UI python=3.11
conda activate RBA-UI
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

Current main dependencies:

```text
PyQt6
requests
python-dotenv
```

### 4) Create local environment file

Copy the example environment file:

```bash
cp .env.example .env
```

Update `.env`:

```env
BACKEND_BASE_URL=http://127.0.0.1:8000
FIREBASE_WEB_API_KEY=PASTE_YOUR_FIREBASE_WEB_API_KEY_HERE
FIREBASE_PROJECT_ID=PASTE_YOUR_FIREBASE_PROJECT_ID_HERE
```

Never commit `.env`.

---

## Firebase Setup

### 1) Create Firebase project

Create a Firebase project from Firebase Console.

### 2) Enable Authentication

Go to:

```text
Build → Authentication → Sign-in method
```

Enable:

```text
Email/Password
```

Do not add signup to the UI. Users should be created by an administrator.

### 3) Register a Web App

In Firebase project settings, register a web app to access the Firebase web config.

Copy the Web API key into `.env`:

```env
FIREBASE_WEB_API_KEY=your_key_here
```

### 4) Enable Firestore

Go to:

```text
Build → Firestore Database
```

Create the database.

### 5) Create user profile document

For each Firebase Auth user, create a Firestore document:

```text
users/{Firebase_User_UID}
```

Required fields:

```text
email: string
mustChangePassword: boolean
```

Example:

```text
email = user@example.com
mustChangePassword = true
```

If `mustChangePassword` is true, the app asks the user to create a new password after login. After successful password update, the app sets this field to false.

### 6) Firestore rules for current UI

The UI directly reads and updates only the logged-in user's document.

Recommended current rules:

```js
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, update: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

Later, this can be moved behind the backend using Firebase Admin SDK.

---

## Backend Setup Requirement

Before launching the UI, start the backend from the RodentBehaviourAnalysis backend repository:

```bash
./start_backend.sh
```

Verify backend health:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","service":"rodent-ml-api-backend"}
```

---

## Run the UI

From the UI project root:

```bash
python -m src.main
```

The app opens the login screen first.

---

## Login Workflow

### Normal login

1. Enter email and password.
2. App logs in through Firebase Authentication.
3. App reads the user's Firestore profile.
4. If `mustChangePassword` is false, the main app opens.

### First-login password change

If Firestore has:

```text
mustChangePassword = true
```

then after login:

1. New password and confirm password fields appear.
2. New password field turns green when it meets the minimum validation.
3. Confirm password field turns green only when it exactly matches.
4. App updates the password in Firebase Auth.
5. App updates Firestore `mustChangePassword` to false.
6. Main app opens.

### Forgot password

The login page includes a forgot-password action.

Flow:

1. User enters their email.
2. User clicks forgot password.
3. Firebase sends a reset email if the email exists.
4. User changes password through Firebase's email reset flow.

---

## Configuration

Environment variables are loaded from `.env` through `python-dotenv`.

Required variables:

```env
BACKEND_BASE_URL=http://127.0.0.1:8000
FIREBASE_WEB_API_KEY=your_firebase_web_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
```

App sizing and polling currently live in `src/config.py`:

```python
POLL_INTERVAL_MS = 3000
APP_WIDTH = 1280
APP_HEIGHT = 800
```

---

## Process Tab Workflow

### 1) Browse folder

Click:

```text
Browse Folder
```

The app scans the selected folder and lists supported videos.

Supported formats:

```text
.mp4
.mov
.avi
.mkv
.m4v
```

Only filenames are shown in the UI, not full paths.

### 2) Select videos

Each video appears with a checkbox.

Use:

```text
Select all videos
```

to select or deselect all listed videos.

### 3) Add videos to queue

Click:

```text
Add to Queue
```

Selected videos are uploaded to the backend and submitted as jobs.

The UI allows adding more videos to the queue even while existing jobs are processing. The backend queue processes jobs chronologically.

### 4) Monitor job cards

Each uploaded video gets a reusable job card showing:

```text
Number
Name
Status
Progress bar
Download button
```

Example statuses:

```text
queued
processing
completed
downloaded
expired
failed
```

### 5) Download result

When a job reaches:

```text
completed
```

the Download button becomes active.

By default, downloads are saved to the user's Downloads folder.

After download, the backend deletes the ZIP and marks the job as downloaded.

---

## Backend Interaction

The UI currently uses these backend API calls:

### Health check

```http
GET /health
```

### Upload video

```http
POST /jobs/upload-video
```

The UI sends the selected file as multipart form data.

### Check job status

```http
GET /jobs/{job_id}/status
```

The UI polls this endpoint every few seconds.

### Download result

```http
GET /jobs/{job_id}/download
```

The backend returns a ZIP result and deletes the backend ZIP after successful download.

---

## Theme System

The UI supports both:

```text
Light mode
Dark mode
```

Colors are centralized in:

```text
src/ui/theme.py
```

Current color strategy:

- 60% main/background color
- 30% surface/card foreground
- 10% accent color

Light theme:

```text
Background: #F7F8FA
Surface:    #FFFFFF
Text:       #111827
Accent:     #B7F000
Orange:     #FE5E00
```

Dark theme:

```text
Background: #0F172A
Surface:    #111827
Text:       #F9FAFB
Accent:     #B7F000
```

Theme assets:

```text
assets/moon.png
assets/sun.png
assets/people-4.png
```

---

## Development Notes

### Remove generated cache files

```bash
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name ".DS_Store" -delete
```

### Recommended `.gitignore`

```gitignore
__pycache__/
*.pyc
.env
.DS_Store
.idea/
dist/
build/
*.spec
```

### Run app

```bash
python -m src.main
```

---

## Known Limitations

- The current Stop button only stops local UI upload/polling.
- Jobs already submitted to the backend may continue processing.
- True backend cancellation requires a backend cancel endpoint.
- Progress bars are currently status-based, not real percentage progress from the ML pipeline.
- Backend API is not yet protected by Firebase ID token verification.
- Firestore user profile is currently accessed directly from the UI.
- Visualize tab is currently planned but not complete.
- Packaged installers are not yet created.

---

## Future Architecture

Planned production flow:

```text
Login Page
   ↓
Firebase Auth
   ↓
Firestore user profile / backend user profile
   ↓
Main App Shell
   ↓
Process Tab / Visualize Tab
   ↓
Protected Backend API
   ↓
Redis Queue + ML Worker
   ↓
Download Processed Results
```

Security goals:

- Firebase Auth login
- Firestore-backed profile flags
- No public signup
- Admin-created users only
- Firebase ID token attached to backend requests
- Backend verifies Firebase ID token
- User-specific job records
- Backend-owned Firestore/Admin SDK access

---

## Typical Git Workflow

```bash
git status
git add -A
git commit -m "Describe your change"
git push
```

Before committing, make sure generated/private files are not staged:

```bash
git status
```

Do not commit:

```text
.env
__pycache__/
*.pyc
local downloaded ZIP files
build artifacts
.idea/
```

---

## Summary

This UI project is the user-facing desktop client for the RodentBehaviourAnalysis backend. The current version supports Firebase-authenticated access, first-login password change, folder-based video selection, backend queue submission, job monitoring, and result downloads. The next major milestones are backend token protection, job cancellation, visualization, packaging, and production deployment.
