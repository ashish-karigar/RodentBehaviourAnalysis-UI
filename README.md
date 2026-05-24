# RodentBehaviourAnalysis UI

A desktop client for uploading rodent maze videos to the RodentBehaviourAnalysis backend, tracking backend processing jobs, and downloading processed result packages.

The UI is designed to be a lightweight installable application for macOS and Windows. It connects to a hosted/local FastAPI backend that runs the actual ML pipeline using DeepLabCut, YOLOv8 maze/zone detection, Redis queueing, and SQLite job tracking.

---

## Abstract

Rodent behavior analysis workflows often involve large raw videos, heavy ML processing, and multiple output artifacts such as cropped videos, tracking files, segmented clips, and Excel reports. Running the full pipeline directly from a local UI can overload user machines and complicate setup.

This UI separates the user-facing workflow from the ML processing workload. Users select a folder of raw videos, add selected videos to a backend queue, monitor each job, and download the processed ZIP result after completion. The backend handles processing sequentially so the ML system is not overloaded.

---

## Introduction

The goal of this desktop UI is to make the RodentBehaviourAnalysis pipeline easier to use for non-technical or semi-technical users.

Current UI workflow:

1. Open the app.
2. Connect to the backend.
3. Browse and select a folder containing raw videos.
4. View supported videos with checkboxes.
5. Add selected videos to the processing queue.
6. Monitor one reusable job card per video.
7. Download completed result ZIP files.
8. Re-add more videos while existing jobs are still processing.

The UI currently focuses on the **Process** tab. A future **Visualize** tab will allow users to inspect processed segment videos and spreadsheet outputs.

---

## Current Status

Implemented:

- PyQt6 desktop UI
- Light/dark theme support
- Folder-based video discovery
- Checkbox-based video selection
- Multi-video queue submission
- Reusable job cards
- Status polling
- Backend upload integration
- Result ZIP download
- Download button states:
  - queued/expired: disabled muted button
  - processing: disabled warning button
  - completed: active green download button
  - downloaded: disabled button with green outline
- Default download location set to the user's Downloads folder

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

- Authentication page before the main UI
- AWS Cognito login/signup integration
- JWT-based backend protection
- User menu and logout support
- Persistent user session
- Better job history screen
- Backend job cancellation endpoint
- True cancel/stop support for already-submitted backend jobs
- Visualize tab for reviewing processed outputs
- Packaged installers for macOS and Windows
- Configurable backend URL
- Error recovery for expired/downloaded jobs
- Improved progress reporting from backend if available

---

## Project Structure

```text
RodentBehaviourAnalysis-UI/
├─ README.md
├─ requirements.txt
├─ assets/
└─ src/
   ├─ main.py
   ├─ api_client.py
   ├─ config.py
   └─ ui/
      ├─ app_window.py
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
  Starts the PyQt6 application.

- `src/ui/app_window.py`  
  Main application shell with top bar, tabs, and theme toggle.

- `src/ui/pages/process_page.py`  
  Main processing workflow: browse folder, select videos, add to queue, monitor jobs, download results.

- `src/ui/components/job_card.py`  
  Reusable processing queue card for each uploaded video.

- `src/ui/theme.py`  
  Centralized light/dark theme and shared stylesheet.

- `src/api_client.py`  
  Handles HTTP communication with the backend API.

- `src/config.py`  
  Stores backend URL and UI polling interval.

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

Current dependencies:

```text
PyQt6
requests
```

### 4) Confirm backend is running

Before launching the UI, start the backend from the RodentBehaviourAnalysis backend repository:

```bash
./start_backend.sh
```

Then verify:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","service":"rodent-ml-api-backend"}
```

### 5) Run the UI

From the UI project root:

```bash
python -m src.main
```

---

## Configuration

Open:

```text
src/config.py
```

Current values:

```python
BACKEND_BASE_URL = "http://127.0.0.1:8000"
POLL_INTERVAL_MS = 3000
```

Change `BACKEND_BASE_URL` when pointing the UI to a hosted backend machine.

Example:

```python
BACKEND_BASE_URL = "http://your-backend-ip:8000"
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

The UI allows adding more videos to the queue even while existing jobs are processing. The backend queue processes them chronologically.

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

The UI uses these backend API calls:

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
```

Dark theme:

```text
Background: #0F172A
Surface:    #111827
Text:       #F9FAFB
Accent:     #B7F000
```

---

## Development Notes

### Remove generated cache files

```bash
find src -type d -name "__pycache__" -prune -exec rm -rf {} +
```

### Recommended `.gitignore`

```gitignore
__pycache__/
*.pyc
.env
.DS_Store
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
- Authentication is not implemented yet.
- Visualize tab is currently planned but not complete.
- Backend URL is currently configured manually in `src/config.py`.

---

## Future Architecture

Planned production flow:

```text
Login Page
   ↓
AWS Cognito Auth
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

Auth goals:

- AWS Cognito user pool
- Signup/login
- JWT token storage
- Token attached to backend requests
- Backend JWT verification
- User-specific job visibility

---

## Typical Git Workflow

```bash
git status
git add -A
git commit -m "Describe your change"
git push
```

Before committing, make sure generated files are not staged:

```bash
git status
```

Do not commit:

```text
__pycache__/
*.pyc
local downloaded ZIP files
build artifacts
.env
```

---

## Summary

This UI project is the user-facing desktop client for the RodentBehaviourAnalysis backend. The current version supports the full process workflow: select videos, submit to backend queue, monitor job status, and download processed results. The next major milestones are authentication, backend protection, packaging, and visualization.
