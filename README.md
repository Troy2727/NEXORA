<div align="center">

<img src="web/assets/logo.svg" width="76" alt="NEXORA logo">

# NEXORA

**Move every task from idea to done.**

A full-stack task manager with a FastAPI + PostgreSQL backend and a fast, dependency-free web dashboard:<br>
kanban board, calendar, reports, time tracking, goals, team chat and per-user privacy built in.

[![Python 3.11](https://img.shields.io/badge/Python%203.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI 0.115](https://img.shields.io/badge/FastAPI%200.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pydantic 2](https://img.shields.io/badge/Pydantic%202-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![SQLAlchemy 2](https://img.shields.io/badge/SQLAlchemy%202-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-555555?style=flat-square)](https://alembic.sqlalchemy.org)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-555555?style=flat-square)](https://www.uvicorn.org)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white)](https://gunicorn.org)
[![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io)
[![PostgreSQL 14](https://img.shields.io/badge/PostgreSQL%2014-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Neon](https://img.shields.io/badge/Neon-34D59A?style=flat-square&logo=neon&logoColor=black)](https://neon.tech)
[![Redis](https://img.shields.io/badge/Redis-FF4438?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Upstash](https://img.shields.io/badge/Upstash-01110D?style=flat-square&logo=upstash&logoColor=00E9A3)](https://upstash.com)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/docs/Web/HTML)
[![CSS](https://img.shields.io/badge/CSS-663399?style=flat-square&logo=css&logoColor=white)](https://developer.mozilla.org/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)](https://docs.pytest.org)
[![Black](https://img.shields.io/badge/Black-000000?style=flat-square&logo=black&logoColor=white)](https://github.com/psf/black)
[![isort](https://img.shields.io/badge/isort-1674B1?style=flat-square)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/badge/Ruff-D7FF64?style=flat-square&logo=ruff&logoColor=black)](https://github.com/astral-sh/ruff)
[![Pyright](https://img.shields.io/badge/Pyright-555555?style=flat-square)](https://github.com/microsoft/pyright)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com)
[![CI/CD Pipeline](https://github.com/Troy2727/NEXORA/actions/workflows/ci.yml/badge.svg)](https://github.com/Troy2727/NEXORA/actions/workflows/ci.yml)

[Features](#-features) · [Screenshots](#-screenshots) · [Quick start](#-quick-start) · [Architecture](#-architecture) · [API](#-api-reference) · [Development](#-development)

<br>

<img src="docs/screenshots/landing.webp" alt="NEXORA landing page" width="100%">

</div>

---

## <img src="docs/icons/sparkles.svg" width="24" height="24" alt="" /> Features

| | |
|---|---|
| **Kanban board** | To do → In progress → Completed with enforced status rules, search, due dates and overdue highlighting. |
| **Overview dashboard** | Today's focus, progress, 7-day activity chart with week-over-week change, status donut, recent activity and what's up next. |
| **Calendar** | Week view with hour grid and a live "now" line, mini month calendar, *Next up* list with tick-to-complete. |
| **Reports** | Key numbers, tasks created per week, status breakdown, overdue list and **CSV export** (formula-injection safe). |
| **Time & goals** | Focus timer per task with daily/weekly totals, weekly completion goal and daily focus goal. |
| **Team & messages** | Create a team, invite people by email, roles (owner/member), and a team chat with unread badges. |
| **Accounts** | Email-verified sign-up, profile photo upload, name and password changes, account deletion, start-page preference. |
| **Privacy by default** | Every task belongs to its owner, other users get `404` for tasks that aren't theirs, and team data is members-only. |
| **Polished UI** | Dark, responsive design that works on phones, keyboard shortcuts (`N`, `/`), SVG icons and accessible contrast. |

## <img src="docs/icons/image.svg" width="24" height="24" alt="" /> Screenshots

**Overview**: today's focus, progress, activity, status breakdown and what's next

<img src="docs/screenshots/overview.webp" alt="Overview dashboard" width="100%">

**Board**: tasks move through clear status rules, with due dates and overdue highlighting

<img src="docs/screenshots/board.webp" alt="Kanban board" width="100%">

**Calendar**: due dates on a week grid, with a mini calendar and a Next up list

<img src="docs/screenshots/calendar.webp" alt="Calendar week view" width="100%">

**Team**: members, roles, invites and an avatar group

<img src="docs/screenshots/team.webp" alt="Team page" width="100%">

**Messages**: team chat with unread badges

<img src="docs/screenshots/messages.webp" alt="Team chat" width="100%">

**Reports**: live numbers, tasks per week and CSV export

<img src="docs/screenshots/reports.webp" alt="Reports" width="100%">

**On phones**

<img src="docs/screenshots/mobile.webp" alt="NEXORA on mobile: overview, board and messages" width="100%">

<details>
<summary><b>More screens: Settings, Time, Goals, Sign in</b></summary>
<br>

**Settings**: profile, password, preferences and account

<img src="docs/screenshots/settings.webp" alt="Settings" width="100%">

**Time**: focus timer and totals

<img src="docs/screenshots/time.webp" alt="Time tracking" width="100%">

**Goals**: weekly and daily targets

<img src="docs/screenshots/goals.webp" alt="Goals" width="100%">

**Sign in**

<img src="docs/screenshots/signin.webp" alt="Sign-in page" width="100%">

</details>

## <img src="docs/icons/rocket.svg" width="24" height="24" alt="" /> Quick start

**Requirements:** Docker and Docker Compose (for the API), and Python 3 (any version) to serve the web app.

```bash
# 1. Configure the API
cp .env.example .env          # then edit the values; change AUTH_SECRET_KEY before deploying

# 2. Start the API, PostgreSQL, Redis and MailCatcher (migrations run automatically)
docker compose up --build

# 3. Serve the web app (no build step needed)
python -m http.server 5173 --directory web
```

| Service | URL |
|---|---|
| Web app | http://localhost:5173 |
| API docs (Swagger UI) | http://localhost:8000/docs |
| Test inbox (MailCatcher) | http://localhost:1080 |

Create an account at **Get started**, open the test inbox to read your 6-digit verification code, and you're in.

> The web app talks to `http://localhost:8000` by default. To point it at another API, run
> `localStorage.setItem("nexora_api", "https://your-api")` in the browser console.

## <img src="docs/icons/cloud-upload.svg" width="24" height="24" alt="" /> Deploy

| Part | Where | How |
|---|---|---|
| Web app | Vercel: **https://nexora-five-dun.vercel.app** | `vercel deploy --prod` from `web/` (static, no build) |
| API | Vercel: **https://nexora-api-smoky.vercel.app** ([docs](https://nexora-api-smoky.vercel.app/docs)) | `vercel deploy --prod` from the repo root (FastAPI preset, `requirements.txt`) |
| PostgreSQL + Redis | Neon and Upstash, connected to the API project from the Vercel Marketplace | `vercel integration add neon` / `vercel integration add upstash/upstash-kv` |

The API reads Neon's `PGHOST_UNPOOLED`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` and Upstash's `REDIS_URL`
directly. Migrations don't run on deploy; after adding one, run
`vercel env run -e production -- python -m alembic upgrade head` from the repo root. Set `AUTH_SECRET_KEY`
and, for verification emails, `SMTP_HOST`, `SMTP_PORT` (465), `SMTP_SSL` (true), `SMTP_USERNAME` and
`SMTP_PASSWORD` with `vercel env add`.

## <img src="docs/icons/network.svg" width="24" height="24" alt="" /> Architecture

![NEXORA architecture: the web app calls FastAPI routers over REST with JWT; routers pass requests to use cases (business rules), which use repositories to reach PostgreSQL, store verification codes in Redis and send email over SMTP.](docs/diagrams/renders/architecture.gif "Click to see full size")

<p align="center"><sub>Click the diagram to see it full size.</sub></p>

<details>
<summary>Editable Mermaid version</summary>

```mermaid
flowchart LR
    subgraph Browser
        W["NEXORA web app<br/>HTML · CSS · ES modules"]
    end
    subgraph API["FastAPI service"]
        R["Routers<br/>auth · user · task · team"] --> U["Use cases<br/>business rules"] --> RP["Repositories<br/>SQLAlchemy 2 async"]
    end
    W -- "REST + JWT (Bearer)" --> R
    RP --> PG[("PostgreSQL 14")]
    U -- "verification codes" --> RD[("Redis")]
    U -- "verification email" --> SM["SMTP<br/>MailCatcher in dev"]
```

</details>

The backend is layered: **routers** handle HTTP and validation (Pydantic), **use cases** hold the rules
(ownership, permissions, status transitions), and **repositories** talk to the database. Alembic manages
the schema. The frontend is a static site with no build step: one ES module per screen, an SVG icon sprite,
and a small API client.

### Data model

![NEXORA data model: users own tasks, join at most one team through team members, and write messages; teams have members, send invites and contain messages.](docs/diagrams/renders/data-model.gif "Click to see full size")

<p align="center"><sub>Click the diagram to see it full size.</sub></p>

<details>
<summary>Editable Mermaid version</summary>

```mermaid
erDiagram
    USERS ||--o{ TASKS : owns
    USERS ||--o| TEAM_MEMBERS : "belongs to (max one team)"
    TEAMS ||--|{ TEAM_MEMBERS : has
    TEAMS ||--o{ TEAM_INVITES : sends
    TEAMS ||--o{ MESSAGES : contains
    USERS |o--o{ MESSAGES : writes

    USERS {
        int id PK
        string email
        string hashed_password
        string first_name
        string last_name
        text avatar "profile photo (data URL)"
        datetime last_login
    }
    TASKS {
        int id PK
        int user_id FK
        string title
        string description
        enum status "created | in_progress | completed"
        datetime due_at
    }
    TEAMS {
        int id PK
        string name
        int owner_id FK
    }
    TEAM_MEMBERS {
        int id PK
        int team_id FK
        int user_id FK "unique"
        enum role "owner | member"
    }
    TEAM_INVITES {
        int id PK
        int team_id FK
        string email
        int invited_by FK
    }
    MESSAGES {
        int id PK
        int team_id FK
        int user_id FK "null after account deletion"
        text body
    }
```

</details>

The animated diagrams are HyperFrames compositions in `docs/diagrams/compositions/`; `docs/diagrams/index.html` lists the commands that render them to `docs/diagrams/renders/`.

### Task lifecycle

![NEXORA task lifecycle: a new task starts in To do (created); Start moves it to In progress; Complete moves To do or In progress to Done (completed); Move to to-do sends In progress back; Reopen sends Done back to To do.](docs/diagrams/renders/task-lifecycle.gif "Click to see full size")

<p align="center"><sub>Click the diagram to see it full size.</sub></p>

<details>
<summary>Editable Mermaid version</summary>

```mermaid
stateDiagram-v2
    direction LR
    [*] --> created: create task
    created --> in_progress: Start
    created --> completed: Complete
    in_progress --> created: Move to to-do
    in_progress --> completed: Complete
    completed --> created: Reopen
```

</details>

Transitions are enforced by the API (`PATCH /task/transitions/{id}/{status}`); anything else returns `400`.

### Sign-up and verification

![NEXORA sign-up: the user creates an account in the web app, which registers with the API and asks for a code; the API stores a 6-digit code in Redis and emails it; the user enters the code, the web app verifies it and logs in, and the API returns a JWT used for later requests.](docs/diagrams/renders/signup-flow.gif "Click to see full size")

<p align="center"><sub>Click the diagram to see it full size.</sub></p>

<details>
<summary>Editable Mermaid version</summary>

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant W as Web app
    participant A as API
    participant R as Redis
    participant M as Mail (SMTP)
    U->>W: Create account
    W->>A: POST /auth/register
    W->>A: POST /auth/send/{email}/code
    A->>R: Store 6-digit code (short TTL)
    A->>M: Email the code
    U->>W: Enter code
    W->>A: POST /auth/verify/{email}/{code}
    A->>R: Check code
    W->>A: POST /auth/login
    A-->>W: JWT access token
    W->>A: Authenticated requests (Bearer token)
```

</details>

## <img src="docs/icons/layers.svg" width="24" height="24" alt="" /> Tech stack

**Backend**<br/>
[![Python 3.11](https://img.shields.io/badge/Python%203.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI 0.115](https://img.shields.io/badge/FastAPI%200.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pydantic 2](https://img.shields.io/badge/Pydantic%202-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![SQLAlchemy 2](https://img.shields.io/badge/SQLAlchemy%202-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-555555?style=flat-square)](https://alembic.sqlalchemy.org)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-555555?style=flat-square)](https://www.uvicorn.org)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white)](https://gunicorn.org)
[![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io)

**Data**<br/>
[![PostgreSQL 14](https://img.shields.io/badge/PostgreSQL%2014-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Neon](https://img.shields.io/badge/Neon-34D59A?style=flat-square&logo=neon&logoColor=black)](https://neon.tech)
[![Redis](https://img.shields.io/badge/Redis-FF4438?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Upstash](https://img.shields.io/badge/Upstash-01110D?style=flat-square&logo=upstash&logoColor=00E9A3)](https://upstash.com)

**Web app**<br/>
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/docs/Web/HTML)
[![CSS](https://img.shields.io/badge/CSS-663399?style=flat-square&logo=css&logoColor=white)](https://developer.mozilla.org/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)

**Quality & deploy**<br/>
[![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)](https://docs.pytest.org)
[![Black](https://img.shields.io/badge/Black-000000?style=flat-square&logo=black&logoColor=white)](https://github.com/psf/black)
[![isort](https://img.shields.io/badge/isort-1674B1?style=flat-square)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/badge/Ruff-D7FF64?style=flat-square&logo=ruff&logoColor=black)](https://github.com/astral-sh/ruff)
[![Pyright](https://img.shields.io/badge/Pyright-555555?style=flat-square)](https://github.com/microsoft/pyright)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com)

| Layer | Technology |
|---|---|
| API | FastAPI 0.115, Pydantic 2, Uvicorn/Gunicorn |
| Database | PostgreSQL 14, SQLAlchemy 2 (async, asyncpg), Alembic |
| Auth | JWT (python-jose), bcrypt password hashing (passlib), email verification via Redis + SMTP |
| Web app | Vanilla HTML, CSS and JavaScript ES modules, inline SVG charts, SVG icon sprite |
| Quality | pytest + pytest-asyncio, black, isort, ruff, pyright, GitHub Actions CI |
| Runtime | Docker, Docker Compose |

## <img src="docs/icons/settings.svg" width="24" height="24" alt="" /> Configuration

Settings are read from environment variables (or `.env`). Defaults are for local development only.

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` · `DB_PORT` | `localhost` · `5432` | PostgreSQL address |
| `DB_LOGIN` · `DB_PASSWORD` · `DB_NAME` | `postgres` · `postgres` · `auth` | PostgreSQL credentials and database |
| `REDIS_HOST` · `REDIS_PORT` · `REDIS_DB` | `redis` · `6379` · `0` | Redis for verification codes |
| `SMTP_HOST` · `SMTP_PORT` | `mailcatcher` · `1025` | Mail server for verification emails |
| `SMTP_SSL` · `SMTP_USERNAME` · `SMTP_PASSWORD` | `false` · `noreply@example.com` · empty | SMTP security and login |
| `AUTH_SECRET_KEY` | `secret` | **JWT signing key, change this in every real deployment** |
| `AUTH_ALGORITHM` | `HS256` | JWT algorithm |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Session length |
| `AUTH_VERIFY_CODE_TTL` | `60` | Seconds a verification code stays valid |

## <img src="docs/icons/braces.svg" width="24" height="24" alt="" /> API reference

Interactive docs live at **`/docs`**. All endpoints except sign-up and login need `Authorization: Bearer <token>`.

<details open>
<summary><b>Auth</b></summary>

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create an account |
| `POST` | `/auth/send/{email}/code` | Email a verification code |
| `POST` | `/auth/verify/{email}/{code}` | Verify the email address |
| `POST` | `/auth/login` | Sign in and get a JWT |

</details>

<details>
<summary><b>User</b></summary>

| Method | Path | Description |
|---|---|---|
| `GET` | `/user/me` | Current account |
| `PATCH` | `/user/me` | Change first/last name |
| `PUT` | `/user/me/password` | Change password (needs the current one) |
| `DELETE` | `/user/me` | Delete the account and all its tasks (needs the password) |
| `PUT` · `DELETE` | `/user/me/avatar` | Upload or remove the profile photo (PNG/JPEG/WebP, max 256 KB, content-checked) |

</details>

<details>
<summary><b>Tasks</b></summary>

| Method | Path | Description |
|---|---|---|
| `POST` | `/task` | Create a task (optional `due_at`) |
| `GET` | `/task/list` | Your tasks |
| `GET` · `PATCH` · `DELETE` | `/task/{id}` | Read, edit (send `due_at: null` to clear) or delete one of your tasks |
| `GET` | `/task/transitions/{id}` | Allowed next statuses |
| `PATCH` | `/task/transitions/{id}/{status}` | Move a task to a new status |

</details>

<details>
<summary><b>Team &amp; messages</b></summary>

| Method | Path | Description |
|---|---|---|
| `GET` · `POST` · `PATCH` · `DELETE` | `/team` | Your team: view, create, rename, delete (owner) |
| `POST` | `/team/invites` | Invite an email address (owner) |
| `DELETE` | `/team/invites/{id}` | Cancel an invite (owner) |
| `GET` | `/team/invites/mine` | Invites sent to you |
| `POST` | `/team/invites/{id}/accept` · `/decline` | Answer an invite |
| `DELETE` | `/team/members/{user_id}` | Remove a member (owner) |
| `POST` | `/team/leave` | Leave your team (members) |
| `GET` · `POST` | `/team/messages` | Read (`?after_id=` for new ones) or post to the team chat |

</details>

## <img src="docs/icons/folder-tree.svg" width="24" height="24" alt="" /> Project structure

```text
NEXORA/
├── api/
│   ├── routers/          # HTTP endpoints: auth, user, task, team
│   ├── schemas/          # Pydantic request/response models and validation
│   └── dependencies/     # DB session, current user, use-case factories
├── usecases/             # Business rules: auth, tasks, users, teams
├── db/
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access
│   └── alembic/          # Migrations
├── enums/  exceptions/  settings/  utils/
├── tests/                # API tests (pytest, in-memory SQLite)
├── web/                  # Frontend (no build step)
│   ├── index.html        # Landing page
│   ├── auth.html         # Sign in / sign up / verify
│   ├── app.html          # Dashboard
│   ├── js/               # One ES module per screen + API client
│   ├── css/              # Base, landing, app, calendar, pages, team
│   └── assets/           # Logo, wordmark, SVG icon sprite
├── docs/screenshots/     # Images used in this README
├── docker-compose.yml  Dockerfile  entrypoint.sh
└── pyproject.toml
```

## <img src="docs/icons/square-terminal.svg" width="24" height="24" alt="" /> Development

```bash
poetry install --with dev,test   # install dependencies
pre-commit install               # format and lint on every commit

poetry run pytest -v             # run the test suite
poetry run black --check . && poetry run isort --check-only .
poetry run ruff check . && poetry run pyright .
```

The same checks run in [GitHub Actions](.github/workflows/ci.yml) on every push and pull request to `master`.
Tests cover authentication, task ownership (users can never see or change each other's tasks), due dates,
profile photos, account settings and every team permission rule.

## <img src="docs/icons/shield-check.svg" width="24" height="24" alt="" /> Security

- **Ownership checks everywhere:** tasks are scoped to their owner; requests for someone else's task return `404`, so they don't reveal that it exists.
- **Team permissions:** only members can read team data and chat; only the owner can invite, remove, rename or delete.
- **Passwords:** hashed with bcrypt; changing the password or deleting the account requires the current password.
- **Uploads:** profile photos are limited to PNG/JPEG/WebP, checked by their actual bytes (not just the name), and capped at 256 KB; SVG is rejected.
- **Output safety:** all user content is escaped in the web app, and CSV exports neutralise spreadsheet formulas.

## <img src="docs/icons/map.svg" width="24" height="24" alt="" /> Roadmap

- [ ] Shared team tasks and assigning tasks to teammates
- [ ] Changing your email with re-verification
- [ ] Notifications (the bell in the header)
- [ ] Real-time chat over WebSockets (currently refreshes every 5 seconds)
- [ ] Storing time entries and goals on the server (currently saved in the browser)

## <img src="docs/icons/user.svg" width="24" height="24" alt="" /> Author

Built by **Alex Mieses** ([@Troy2727](https://github.com/Troy2727)).

Alex built NEXORA as a complete product, not just an API: a layered FastAPI backend on PostgreSQL, email
verification through Redis and SMTP, and a dependency-free web app with a kanban board, calendar, reports,
time tracking, goals and team chat. Ownership and team permission rules are enforced by the server and covered
by tests, every push runs CI (tests, formatting, linting and type checks), and both the web app and the API
are live on Vercel.

Released under the [MIT License](LICENSE).
