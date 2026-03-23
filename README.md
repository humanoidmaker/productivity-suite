# Productivity Suite — Self-Hosted Productivity Suite

A full-stack, self-hosted office platform with three core applications:

- **DocFlow** — Word processor (TipTap/ProseMirror rich text editor)
- **GridCalc** — Spreadsheet (custom virtual-scrolling grid with 70+ formula functions)
- **DeckBuilder** — Presentations (canvas-based slide editor with slideshow mode)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.12, FastAPI, uvicorn |
| Database | PostgreSQL 16 |
| Cache/PubSub | Redis 7 |
| Task Queue | Celery + Redis |
| File Storage | MinIO (S3-compatible) |
| Real-time | WebSocket + Yjs CRDT |
| Frontend App | React 18 + TypeScript + Vite + Tailwind CSS |
| Frontend Admin | React 18 + TypeScript + Vite + Tailwind CSS + Recharts |
| Document Editor | TipTap (ProseMirror) |
| Export | python-docx, openpyxl, python-pptx, WeasyPrint |
| Containerization | Docker + Docker Compose |
| Orchestration | Kubernetes |

## Quick Start

```bash
# Start all services
docker compose up -d

# Seed admin user
python scripts/seed_admin.py

# Initialize MinIO buckets
python scripts/init_minio_buckets.py

# Seed templates
python scripts/seed_templates.py
```

**Access:**
- App: http://localhost:3000
- Admin: http://localhost:3001
- API: http://localhost:8000/api/docs
- MinIO Console: http://localhost:9001

**Default admin:** `admin@productivity.local` / `admin123`

## Project Structure

```
productivity/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # REST API routes
│   │   ├── models/    # SQLAlchemy models (13 tables)
│   │   ├── schemas/   # Pydantic validation
│   │   ├── services/  # Business logic
│   │   ├── formulas/  # Spreadsheet formula engine
│   │   ├── export/    # DOCX/XLSX/PPTX/PDF/CSV/HTML exporters
│   │   ├── importer/  # DOCX/XLSX/CSV/PPTX importers
│   │   ├── collaboration/ # Yjs, WebSocket, presence
│   │   ├── tasks/     # Celery background tasks
│   │   └── middleware/ # Auth, rate limiting, logging
│   └── tests/         # 213+ passing tests
├── frontend-app/      # Main productivity suite UI
│   └── src/
│       ├── pages/     # Login, Home, MyFiles, DocumentEditor, SpreadsheetEditor, PresentationEditor
│       └── components/ # Document, Spreadsheet, Presentation editors + file management
├── frontend-admin/    # Admin panel
│   └── src/
│       └── pages/     # Dashboard, Users, Activity, System Health, Settings
├── k8s/               # Kubernetes manifests
├── scripts/           # Seed & utility scripts
├── docker-compose.yml
├── Makefile
└── README.md
```

## Features

### Document Editor (DocFlow)
- Rich text editing with TipTap/ProseMirror
- Full toolbar: headings, bold/italic/underline, alignment, lists, links, images, code blocks
- A4 page-like rendering
- Word/character count
- Export: DOCX, PDF, HTML, TXT
- Import: DOCX, HTML, TXT
- Auto-save with Ctrl+S

### Spreadsheet Editor (GridCalc)
- Virtual-scrolling grid (renders only visible cells)
- 70+ formula functions: SUM, AVERAGE, VLOOKUP, IF, INDEX/MATCH, and more
- Formula bar with cell reference display
- Cell formatting: bold, italic, colors, alignment, number formats
- Multiple sheets with tab management
- Keyboard navigation: Arrow keys, Tab, Enter, Delete
- Export: XLSX, CSV
- Import: XLSX, CSV

### Presentation Editor (DeckBuilder)
- Canvas-based slide editor with 16:9 / 4:3 aspect ratio
- Elements: text boxes, shapes (rectangle, circle), images
- Drag to move, resize handles, element selection
- Slide thumbnail panel with add/navigate
- Speaker notes per slide
- Full-screen slideshow mode (arrow keys, B for black, W for white, Escape to exit)
- Export: PPTX

### Shared Features
- JWT authentication (access + refresh tokens)
- Folder-based file organization
- File sharing (user-to-user, link sharing, password protection)
- Version history with snapshots
- Comments with threading
- Star/favorite files
- Full-text search
- Trash with auto-purge
- Storage quotas
- Activity logging
- Rate limiting

### Admin Panel
- Dashboard with stats (users, files, storage)
- User management (CRUD, role assignment, quota, enable/disable)
- Activity log viewer
- System health monitoring (PostgreSQL, Redis, MinIO, WebSocket connections)
- Settings viewer

## Running Tests

```bash
# Backend tests (213+ passing)
cd backend && python -m pytest tests/unit/ -v

# Full test suite
bash scripts/run_all_tests.sh
```

## Kubernetes Deployment

```bash
cd k8s && bash deploy.sh
```

Endpoints:
- `app.productivity.local` — Main app
- `admin.productivity.local` — Admin panel
- `api.productivity.local` — API

## License

Private — for educational use.
