# TaskFlow — Detailed Project Reference

This document explains the TaskFlow project in detail: goals, architecture, every important file and function, how data flows, and how to run and extend the project.

---

**Quick summary**
- Backend: Express.js server in `backend/` with JSON-file storage (`backend/data/db.json`).
- Frontend: Streamlit app in `app.py` (Python) used as the main UI.
- Purpose: simple, self-contained task management demo supporting Admin/Manager/Employee roles, tasks, files, messages, reports, and audit logs.
 - Notes: The demo previously had a separate `frontend/` React/Vite app which is deprecated and removed; the maintained UI is the Streamlit `app.py`.
 - Signup fallback: self-registration attempts that fail due to forbidden backend or connectivity issues are saved to `data/pending_signups.json` for admin review.

---

## Table of contents
- Project run instructions
- High-level architecture
- Data model (db.json)
- Backend: file-by-file detailed reference
- Frontend (`app.py`): function-by-function breakdown
- Security and authentication
- Troubleshooting notes
- Extending TaskFlow (recommended changes)

---

## How to run (quick)
1. Install backend deps and seed data:

```powershell
cd backend
npm install
npm run seed
node server.js
```

2. Install Python deps and run the UI from repository root:

```powershell
pip install streamlit requests pandas
streamlit run app.py
```

Backend default: `http://localhost:4000`
Streamlit UI default: `http://localhost:8501`

---

## High-level architecture
- Backend provides a small REST API under `/api/*`.
- The backend uses a lightweight JSON file store implemented in `backend/db.js`. This keeps the project dependency-free for DBs and is suitable for demos.
- The frontend is a Streamlit single-file UI (`app.py`) that calls the backend endpoints using `requests` (via `api_call`).
- Authentication uses JWT tokens and `Authorization: Bearer <token>` headers.

---

## Data model (as stored in `backend/data/db.json`)
The JSON file contains top-level objects:
- `users`: array of user objects { id, email, fullName, role, password (hashed), createdAt }
- `tasks`: array of tasks { id, title, description, assigneeId, status, priority, dueDate, createdBy, createdAt, updatedAt }
- `files`: array with uploaded file objects (content stored Base64)
- `messages`: chat/message entries
- `audit`: action records for audit logs

`backend/db.js` ensures defaults and creates the `db.json` if missing.

---

## Backend — file-by-file
All files live in `backend/`.

### `server.js`
Purpose: Application entry point and route registration.
Key points:
- Configures CORS and JSON body parsing.
- Defines `/api/auth/login` endpoint which validates email/password by comparing hashed password and returns a JSON object `{ token, user }` where `token` is a JWT and `user` is a trimmed user object.
- Mounts routers: `/api/tasks`, `/api/dashboard`, `/api/users`, `/api/files`, `/api/messages`, `/api/reports`, `/api/audit`.
- Starts the HTTP server on `process.env.PORT || 4000`.

Why: Centralizes route wiring and the login endpoint.

---

### `db.js`
Purpose: Minimal JSON file-based persistence layer.
Exports: an object with `.data`, `.read()`, and `.write()`.

Behavior:
- Creates a `backend/data` directory and `db.json` if missing.
- `read()` loads the JSON and sets defaults for expected arrays: `users`, `tasks`, `files`, `messages`, `audit`.
- `write()` writes the in-memory `db.data` back to disk.

Why: Simple persistent store for demo/testing without a real DB.

Notes & risks:
- Designed for demo; concurrent server processes writing the same file could cause race conditions.
- For production use, replace with a database (Postgres/MongoDB).

---

### `auth.js`
Purpose: JWT-based authentication helpers and middleware.
Functions exported:
- `sign(user)`: returns a JWT token signed with `process.env.JWT_SECRET` or fallback secret.
- `verifyToken(token)`: verifies token via `jsonwebtoken`.
- `authMiddleware(req,res,next)`: Express middleware that expects `Authorization: Bearer <token>` and populates `req.user` with token payload. Returns 401 errors on failure.
- `authorize(...roles)`: factory returning middleware that checks `req.user.role` belongs to allowed roles; uses `authMiddleware` internally.

Why: Centralized auth logic used across routes. Keep secret safe in environment variables.

---

### `seed.js`
Purpose: Populate `db.json` with demo users and sample tasks.
What it does:
- Reads DB, creates three users (admin, manager, employee) with passwords (`Admin@123`, `Manager@123`, `Employee@123`) hashed with `bcryptjs`.
- Adds a couple sample tasks assigned to seeded users.
- Writes `db.json` back to disk.

Why: Convenient starting data for demo/testing. Run `npm run seed` before server start.

---

### `routes/tasks.js`
Purpose: Task CRUD API.
Endpoints:
- `GET /api/tasks` — `authMiddleware` required. Returns all tasks sorted by `createdAt` descending.
- `POST /api/tasks` — `authorize('ADMIN', 'MANAGER')` required. Create a task with provided fields; sets `createdBy` from `req.user.id`.
- `PATCH /api/tasks/:id` — `authMiddleware` required. Behavior:
  - If user role is `EMPLOYEE`: allowed to update only the `status` field; `status` must be present in the request body.
  - If user role is ADMIN / MANAGER: allowed to edit any of `title, description, assigneeId, status, priority, dueDate`.
- `DELETE /api/tasks/:id` — `authorize('ADMIN')` required: deletes a task.

Why: Role-based operations ensure managers/admins manage tasks while employees can update status.

Important note: In the demo code employees can update status for any task (not limited to assigned tasks). This design choice prioritizes ease-of-use; for stricter restrictions, the `assigneeId` check can be used.

---

### `routes/users.js`
Purpose: User management endpoints.
Endpoints:
- `GET /api/users` — `authorize('ADMIN')`: returns list of users (id, email, fullName, role, createdAt).
- `POST /api/users/signup` — public endpoint: allows self-registration for `EMPLOYEE` role. Accepts `{ email, fullName, password }`, hashes the password, forces `role: 'EMPLOYEE'`, creates user and an audit entry; returns 201.
- `POST /api/users` — `authorize('ADMIN')`: admin-only create user (any role) with password, writes to DB and audit.
 - `DELETE /api/users/:id` — `authorize('ADMIN','MANAGER')` with additional rules enforced:
   - Admin may delete any user except themselves.
   - Manager may delete users only when the target user's role is `EMPLOYEE`.
   - All deletions append an audit entry. The backend enforces these rules; the Streamlit UI includes a confirmation flow and respects the same role guard.

Why: Provides both admin-managed creation and optional self-service signups for employees.

Security note: The public signup endpoint forces `EMPLOYEE` role, preventing privilege escalation from the signup path.

---

### `routes/dashboard.js`
Purpose: Dashboard summaries.
Endpoint: `GET /api/dashboard/summary` (requires auth). Computes:
- `totalTasks`: number of tasks
- `byStatus`: array of `{ status, cnt }`
- `users`: count of users

Why: Simple aggregation used by frontend to build charts and metrics.

---

### `routes/files.js`
Purpose: Simple file management (content stored Base64 in DB).
Endpoints:
- `POST /api/files` — `authMiddleware` required. Accepts `{ name, contentBase64 }`, stores a file object with `versions` array (first version included), appends audit entry.
- `GET /api/files` — `authMiddleware` required. Returns file summaries.
- `GET /api/files/:id` — `authMiddleware` required. Returns full file object, including content.

Why: Lightweight file storage for demo. For production, replace with a proper storage service (S3, file server) and store metadata in DB.

---

### `routes/messages.js`
Purpose: Team messages / comments.
Endpoints:
- `GET /api/messages?taskId=...` — `authMiddleware` required. Returns messages filtered by `taskId` when provided.
- `POST /api/messages` — `authMiddleware` required. Creates a message entry and an audit entry; expects `{ taskId, text }`.

Why: Allows communication around tasks.

---

### `routes/reports.js`
Purpose: Expose lightweight task reports.
Endpoint: `GET /api/reports/tasks` — `authMiddleware` required.
- Returns JSON summary by default: `{ total, rows }` where rows are simple task objects.
- If `?format=csv` is passed, returns a CSV string with headers.

Why: Provide export functionality for tasks.

---

### `routes/audit.js`
Purpose: Admin-only access to the `audit` array.
- `GET /api/audit` — `authorize('ADMIN')` required. Returns `db.data.audit`.

Why: Keep audit logs visible only to admins.

---

## Frontend — `app.py` (detailed)
`app.py` is a Streamlit single-file frontend. It handles UI, state, and calls backend endpoints.

Top-level module imports:
- `streamlit as st`, `requests`, `pandas`, `datetime`, `json`, `BytesIO`, `base64`.

Page configuration & CSS:
- `st.set_page_config` sets title, icon and layout.
- Custom CSS is injected to style the sidebar and role badges.

Global constants & session state:
- `API_URL = "http://localhost:4000/api"` — backend base url used by the UI.
- `st.session_state` keys initialized: `token`, `user`, `page`.

Helper functions

- `get_headers()`:
  - Returns `{"Authorization": f"Bearer {st.session_state.token}"}` if token exists; otherwise `{}`.
  - Used by `api_call` to add auth headers.

- `api_call(method, endpoint, data=None)`:
  - Central wrapper around `requests` to call the backend.
  - Supports GET, POST, PATCH, DELETE.
  - Uses `get_headers()` for Authorization.
  - Handles `ConnectionError`, `Timeout`, and generic errors by showing Streamlit messages.
  - Returns parsed JSON on success or `None` on handled failures.

- `get_role_badge(role)`:
  - Returns an HTML snippet with a CSS role badge class for inline display.

Login/Signup flow — `login_page()`
- Shows a login form with `email` and `password` inputs.
- On `Login` button: calls `POST /api/auth/login` via `api_call`.
  - On success, stores `token` and `user` in `st.session_state` and reruns the app (so the main app renders).
  - On failure, displays an error.
- `Create Employee Account` expander (signup): collects `fullName`, `email`, `password`, `confirm`.
  - Attempts to `POST /api/users/signup` directly (no auth header). If backend allows, returns 201 and shows success.
  - If the backend returns 403 or is unreachable, signup is saved locally to `data/pending_signups.json` for admin review.

Why this design:
- Keeps the UI simple while allowing both immediate user creation (if backend allows) and fallback when the backend restricts registrations.

Dashboard & pages (high-level)
- The UI is role-aware using `st.session_state.user.role` and `get_role_badge`.
- Pages included: `dashboard_page`, `tasks_page`, `files_page`, `messages_page`, `reports_page`, `employees_page`, `audit_page`.
- Main routing: `main()` shows `login_page()` if not logged in; otherwise a sidebar with navigation and role-specific pages.

Key page behavior

- `dashboard_page()`:
  - Fetches `/tasks`, `/dashboard/summary`, `/users`.
  - Displays metrics and charts. For admins it shows system overview and team charts; for managers and employees it shows relevant task summaries.

- `tasks_page()`:
  - Tabbed UI: All Tasks (with filters) and Create Task (Managers/Admins can create tasks via backend endpoint).
  - Create task calls `POST /api/tasks` using `api_call` (requires ADMIN or MANAGER).

- `files_page()`:
  - Upload flow: collects filename and file, encodes it base64, POSTs to `/api/files`.
  - Lists files via GET `/api/files`.

- `messages_page()`:
  - Lists messages via `GET /api/messages` and allows posting via `POST /api/messages`.

- `reports_page()`:
  - Exports CSV/JSON/Excel-style by calling `/api/reports/tasks` and downloading results.

- `employees_page()`:
  - Admins and managers can view employees.
  - Admins can add employees with a default password via `POST /api/users` (admin endpoint).

- `audit_page()`:
  - Admin-only page to view `GET /api/audit`.

State & UX details
- After login Streamlit reruns the script with the `token` set in `st.session_state` enabling the sidebar and pages.
- Buttons call endpoints and typically `st.rerun()` after successful changes to refresh data.

---

## Security and authentication
- JWTs issued by `auth.sign` are used to authenticate requests.
- `auth.authMiddleware` enforces the presence and format of `Authorization: Bearer <token>`.
- Sensitive actions use `authorize(...)` to restrict roles.
- Passwords are hashed with `bcryptjs` on user creation.

Notes and improvements:
- The demo secret defaults to a development value; set `JWT_SECRET` in env for production.
- The JSON-file DB stores hashed passwords but is not hardened. For production use a proper database and rotate secrets.
- Audit logs are appended to `db.data.audit` for traceability.

---

## Troubleshooting (common issues)
- 401 `Missing auth` on actions: ensure you logged in and `st.session_state.token` is present.
- 403 `Forbidden` when creating users: only admins can create users via `/api/users`; users must use `/api/users/signup` or be created by an admin.
- Backend unreachable: check `node server.js` is running and no firewall is blocking `localhost:4000`.
- File upload large failure: streams are not implemented — file content is fully read into memory and stored base64. Use a proper storage backend for large files.

Testing tips
- Use `npm run seed` to reset demo users and tasks.
- Use `curl` or Postman to test endpoints directly, e.g.:
  - `POST http://localhost:4000/api/auth/login` with demo credentials.
  - `GET http://localhost:4000/api/tasks` with header `Authorization: Bearer <token>`.

---

## Where to look for specific behavior
- Login auth: `backend/server.js` (`/api/auth/login`) and `backend/auth.js` (JWT signing/verify).
- Data persistence: `backend/db.js` (read/write semantics) and `backend/data/db.json` (live data).
- Seeding demo data: `backend/seed.js`.
- Task rules and patching logic: `backend/routes/tasks.js` (employee vs admin behavior).
- User creation rules: `backend/routes/users.js` (admin create + public `/signup`).
- UI pages and integration: `app.py` — each function `login_page`, `dashboard_page`, `tasks_page`, etc. maps to a UI page and calls the backend.

---

## Suggested next improvements (practical roadmap)
1. Replace `db.js` with a proper DB (Postgres / MongoDB) for concurrency and persistence.
2. Use environment-based configuration (ports, JWT secret) more strictly and document `.env` usage.
3. Move file storage to a dedicated storage service (S3) and keep only metadata in DB.
4. Add tests for APIs (Mocha/Jest) and for critical UI workflows.
5. Add admin UI to approve pending signups (if you want signups queued instead of directly created).
6. Add email verification for signups.
7. Harden audit log (append-only store) and add pagination for large audit arrays.

---

## Appendix — quick reference of notable functions
- `backend/db.js`:
  - `read()` — load file, init defaults
  - `write()` — save file

- `backend/auth.js`:
  - `sign(user)`
  - `verifyToken(token)`
  - `authMiddleware(req,res,next)`
  - `authorize(...roles)`

- `backend/routes/tasks.js`:
  - `GET /api/tasks`
  - `POST /api/tasks` (admin/manager)
  - `PATCH /api/tasks/:id` (role-based behavior)
  - `DELETE /api/tasks/:id` (admin)

- `app.py`:
  - `get_headers()`, `api_call()` — central API calling utilities
  - `login_page()` — login & signup UI
    - Signup fallback: If `POST /api/users/signup` fails due to a 403 or connection error, `app.py` saves the request to `data/pending_signups.json`. An Admin can review pending signups from `Employees -> Pending Signups` and approve (creates account with default password `TaskFlow@123`) or reject (removes the pending entry).
    - Delete confirmation: Deleting a user from the Employees view is a two-step flow (click Delete → confirm or cancel). This uses `st.session_state` to avoid accidental deletions.
    - `api_call()` hardening: `api_call()` was updated to handle 204 No Content and non-JSON responses gracefully and to show clearer error messages in the UI.
  - `dashboard_page()` — metrics & charts
  - `tasks_page()` — list & create tasks
  - `files_page()`, `messages_page()`, `reports_page()`, `employees_page()`, `audit_page()` — other views
  - `main()` — routing + sidebar
 - `app.py` changes summary:
   - Removed many decorative emojis from the UI text and replaced them with clear textual labels.
   - `api_call()` improved to handle empty/non-JSON responses and 204 status codes.
   - Employee self-signup fallback implemented: pending signups saved to `data/pending_signups.json` and Admin review UI added in `employees_page()`.
   - Employee deletion support with role-based restrictions and a session-state backed confirmation flow.

---

