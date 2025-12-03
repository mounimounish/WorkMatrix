# TaskFlow Project Structure & File Explanation

## Overview
TaskFlow is an enterprise task management system with a Node.js/Express backend and Streamlit frontend. This document explains the purpose of every file and folder, architectural choices, and why specific technologies were selected.

---

## Project Directory Structure

```
workflow-sysytem/
├── backend/                          # Node.js + Express REST API
│   ├── server.js                     # Application entry point
│   ├── db.js                         # Database abstraction layer
│   ├── auth.js                       # JWT authentication & middleware
│   ├── seed.js                       # Demo data initialization
│   ├── package.json                  # Node dependencies & scripts
│   ├── package-lock.json             # Dependency lock file
│   ├── data/
│   │   └── db.json                   # JSON file-based database
│   └── routes/
│       ├── tasks.js                  # Task CRUD endpoints
│       ├── users.js                  # User management & signup
│       ├── dashboard.js              # Dashboard summary metrics
│       ├── files.js                  # File upload/download
│       ├── messages.js               # Team messaging
│       ├── reports.js                # Report generation & export
│       └── audit.js                  # Audit logging access
│
├── data/                             # Application-level data directory
│   └── pending_signups.json          # Local fallback for failed signups
│
├── app.py                            # Streamlit frontend (main UI)
├── README.md                         # Quick start guide
├── detailed-readme.md                # Detailed technical documentation
├── explanation.md                    # This file - architecture & design decisions
└── .gitignore                        # Git ignore rules
```

---

## File-by-File Explanation

### Root Level Files

#### `app.py`
**Purpose:** Main Streamlit UI application. Single-file Python frontend serving as the primary user interface.

**Why Streamlit?**
- Fast prototyping without complex UI frameworks
- Real-time hot-reload during development
- Simple session state management
- Built-in components (charts, tables, forms)
- Low overhead compared to React/Vue
- Ideal for internal tools and dashboards

**Why not React/Vue/Angular?**
- Would require a separate Node.js/Express frontend server
- Adds build complexity (webpack, bundlers)
- Requires more boilerplate code
- Harder to integrate with Python backend data science workflows
- Streamlit reduces TTM (time to market) for demos

**Key Functions:**
- `get_headers()` - Constructs auth headers with JWT token
- `api_call()` - Central HTTP client for backend calls (handles GET, POST, PATCH, DELETE)
- `login_page()` - User authentication and employee self-signup
- `dashboard_page()` - Role-based metrics and charts
- `tasks_page()` - Task CRUD operations
- `employees_page()` - Admin/Manager user management with delete confirmation and pending signup review
- `audit_page()` - Admin-only audit log viewing
- `main()` - Page routing and sidebar navigation

**State Management:**
- Uses `st.session_state` for:
  - `token` - JWT authentication token
  - `user` - Current logged-in user object
  - `page` - Current active page
  - `confirm_delete` - Two-step delete confirmation state

---

#### `README.md`
**Purpose:** Quick start guide and feature overview for new users.

**Content:**
- Prerequisites and setup commands
- Feature list
- Demo login credentials
- API endpoint reference
- Tech stack summary
- Usage examples
- Configuration notes
- Troubleshooting

**Why have both README.md and detailed-readme.md?**
- README.md is for quick reference and onboarding
- detailed-readme.md is for developers understanding architecture
- Keeps information organized and targeted to different audiences

---

#### `detailed-readme.md`
**Purpose:** In-depth technical documentation for developers.

**Content:**
- High-level architecture
- Data model (database schema)
- Backend file-by-file breakdown
- Frontend function-by-function breakdown
- Security and authentication details
- Troubleshooting advanced issues
- Suggested improvements roadmap

---

#### `explanation.md`
**Purpose:** This file. Explains the complete project structure, design decisions, and why specific technologies/patterns were chosen.

---

### Backend Directory (`backend/`)

#### `server.js`
**Purpose:** Express.js application entry point. Configures middleware and mounts all route handlers.

**Responsibilities:**
- CORS configuration for cross-origin requests from Streamlit UI
- JSON body parser for request handling
- Route mounting (`/api/tasks`, `/api/users`, etc.)
- Login endpoint (`POST /api/auth/login`)
- Error handling middleware
- HTTP server startup on port 4000

**Why Express.js?**
- Lightweight and unopinionated framework
- Minimal setup overhead
- Large ecosystem of middleware
- Perfect for REST APIs
- Good performance
- Easy to learn and extend

**Why not Fastify/Hapi/Django?**
- Fastify: Too low-level, overkill for a demo project
- Hapi: More enterprise-oriented, unnecessary complexity
- Django: Would require Python backend; Node.js chosen for easier deployment

---

#### `db.js`
**Purpose:** Database abstraction layer. Implements a lightweight file-based persistence system using JSON.

**Exports:**
- `db.data` - In-memory data object with keys: `users`, `tasks`, `files`, `messages`, `audit`
- `db.read()` - Load JSON from disk, initialize defaults
- `db.write()` - Persist in-memory data to disk

**Why JSON file storage?**
- Zero external dependencies (no database server)
- Suitable for demos and small datasets
- Easy to inspect data (plain text JSON)
- No schema migrations
- Fast enough for testing and prototyping

**Why not use a real database (PostgreSQL/MongoDB)?**
- Adds deployment complexity (database server setup)
- Not necessary for a demo/proof-of-concept
- JSON storage keeps the project self-contained
- Can be swapped later without API changes

**Limitations & Production Concerns:**
- No concurrency control (race conditions with multiple writers)
- No transactions
- No query optimization
- Entire dataset loaded into memory
- **For production:** Replace `db.read()` / `db.write()` with actual database ORM (Sequelize, TypeORM, Prisma)

---

#### `auth.js`
**Purpose:** JWT-based authentication helpers and Express middleware factories.

**Exports:**
- `sign(user)` - Create JWT token from user object
- `verifyToken(token)` - Validate JWT signature
- `authMiddleware(req, res, next)` - Middleware to parse `Authorization: Bearer <token>` header
- `authorize(...roles)` - Factory returning middleware that checks user role

**Why JWT (JSON Web Tokens)?**
- Stateless authentication (no session storage needed)
- Self-contained credentials (token includes user info)
- Works well with distributed/serverless architectures
- Simple to implement
- No server-side session lookup

**Why not sessions/cookies?**
- Session storage would require Redis or database
- Cookies have CORS restrictions with cross-origin frontends
- JWT is simpler for API-based architecture

**Security Notes:**
- Secret defaults to `"demo-secret"` for development
- Should use environment variable `JWT_SECRET` in production
- Tokens don't expire in this implementation (should add `expiresIn` for production)

---

#### `seed.js`
**Purpose:** Initialization script that populates `db.json` with demo users and sample tasks.

**What it creates:**
- Admin user: `mounishm@rljit.in` / `MOUNI`
- Manager user: `manager@local` / `Manager@123`
- Employee user: `employee@local` / `Employee@123`
- 2 sample tasks with assignments

**Why seed data?**
- Provides immediate demo environment
- Avoids empty database on first run
- Makes testing easier
- Developers can quickly see the app in action

**How it's used:**
- Run manually: `npm run seed`
- Or run `npm run seed` before starting server
- Skips creating duplicate users (safe to run multiple times)

---

#### `package.json`
**Purpose:** Node.js project configuration and dependency management.

**Scripts:**
- `start` - Run server
- `seed` - Initialize demo data
- `dev` - Run with nodemon (auto-restart on file changes)

**Dependencies:**
- `express` - Web framework
- `jsonwebtoken` - JWT signing/verification
- `bcryptjs` - Password hashing
- `nanoid` - Unique ID generation
- `cors` - Cross-origin request handling

**Why these dependencies?**
- express: Standard for Node.js REST APIs
- jsonwebtoken: Industry standard for JWT
- bcryptjs: Secure password hashing (never store plain passwords)
- nanoid: Lightweight, URL-safe ID generator (simpler than UUID)
- cors: Handles requests from Streamlit on different port

---

### Backend Routes Directory (`backend/routes/`)

Each route file handles a specific feature area and is mounted in `server.js`.

#### `tasks.js`
**Purpose:** Task CRUD operations and task-specific business logic.

**Endpoints:**
- `GET /api/tasks` - List all tasks (auth required)
- `POST /api/tasks` - Create task (admin/manager only)
- `PATCH /api/tasks/:id` - Update task (role-based: employees can only update `status`, managers/admins can update all fields)
- `DELETE /api/tasks/:id` - Delete task (admin only)

**Why separate roles for updates?**
- Employees should only mark tasks as done/in-progress
- Managers/admins can modify task details
- Prevents employees from changing priority or assignment accidentally

**Design Pattern:** Role-based authorization at endpoint level using `authorize()` middleware

---

#### `users.js`
**Purpose:** User management, authentication, and employee self-registration.

**Endpoints:**
- `GET /api/users` - List all users (admin only)
- `POST /api/users` - Create user (admin only, any role)
- `POST /api/users/signup` - Public employee self-registration (forces role = `EMPLOYEE`)
- `DELETE /api/users/:id` - Delete user (admin can delete anyone except self; manager can delete only `EMPLOYEE` role users)

**Key Design Decision: Public signup endpoint**
- Allows employees to self-register without admin intervention
- Forced to `EMPLOYEE` role (prevents privilege escalation)
- Returns 403 if public registration is disabled
- UI falls back to local `data/pending_signups.json` when backend rejects signup

**Why separate `/signup` from `/users`?**
- `/users` is admin-only (creates any role)
- `/signup` is public (self-service, forced to employee)
- Allows flexible registration policies

---

#### `dashboard.js`
**Purpose:** Compute and return dashboard summary metrics.

**Endpoints:**
- `GET /api/dashboard/summary` - Returns total tasks, tasks by status, user count

**Used by:**
- `dashboard_page()` in `app.py` to display charts and metrics
- Role-specific views (admin sees system overview, manager sees team, employee sees personal)

**Why separate route?**
- Aggregations computed on backend (not frontend)
- Reusable by multiple frontend views
- Single source of truth for metrics

---

#### `files.js`
**Purpose:** File upload and retrieval with base64 encoding.

**Endpoints:**
- `POST /api/files` - Upload file (auth required)
- `GET /api/files` - List file summaries (auth required)
- `GET /api/files/:id` - Get full file object with content (auth required)

**Design:**
- Files stored as base64-encoded strings in JSON
- `versions` array tracks multiple uploads of same file

**Limitations:**
- Files loaded fully into memory
- Base64 encoding adds ~33% size overhead
- Not suitable for large files

**Why base64 in JSON?**
- Avoids need for separate file storage service
- Keeps everything self-contained
- Simple to implement

**Production Alternative:**
- Use S3, Azure Blob, or similar cloud storage
- Store only file metadata in database
- Serve files directly from storage service

---

#### `messages.js`
**Purpose:** Team messaging and communication logging.

**Endpoints:**
- `GET /api/messages?taskId=...` - Get messages (optionally filtered by task)
- `POST /api/messages` - Create message (auth required)

**Design:**
- Messages can be associated with tasks via `taskId`
- Supports general team chat (no taskId)
- Logged to audit trail

**Why messages feature?**
- Enables team collaboration
- Alternative to email notifications
- Central communication hub

---

#### `reports.js`
**Purpose:** Report generation and export in multiple formats.

**Endpoints:**
- `GET /api/reports/tasks` - Get task report
  - Default: JSON format with `{ total, rows }`
  - `?format=csv` - Returns CSV string with headers

**Supported Exports:**
- JSON (native)
- CSV (text format)
- Excel-style (CSV that opens in Excel)

**Why separate reports route?**
- Aggregation logic isolated from task routes
- Allows multiple export formats
- Easier to add new report types

**Future Enhancements:**
- PDF export
- Filtered reports (by date range, status, etc.)
- Email delivery

---

#### `audit.js`
**Purpose:** Audit log access for admin-only viewing.

**Endpoints:**
- `GET /api/audit` - Get all audit entries (admin only)

**What gets logged:**
- User creation
- User deletion
- Task creation/update/deletion
- File uploads
- Message posts

**Why audit logs?**
- Compliance and security
- Track who did what and when
- Useful for troubleshooting
- Required for regulated industries

**Current Implementation:**
- Append-only array in JSON
- No pagination (could be issue with large datasets)

**Production Improvements:**
- Paginate audit log
- Add filtering by action/user/date
- Store audit in separate database table
- Add retention policies

---

### Data Directory (`data/`)

#### `pending_signups.json`
**Purpose:** Local fallback for employee signup requests when backend rejects them or is unreachable.

**Structure:**
```json
[
  {
    "fullName": "John Doe",
    "email": "john@company.com",
    "requestedAt": "2025-12-04T10:30:00.000Z",
    "note": "backend-unreachable" // optional
  }
]
```

**When used:**
- Employee attempts signup via `POST /api/users/signup`
- Backend returns 403 (forbidden) or connection error occurs
- Signup request is saved locally for admin review

**Admin Workflow:**
1. Login as admin
2. Navigate to Employees page
3. Open "Pending Signups (Local)" expander
4. Approve (creates account) or Reject (removes entry)

**Why local fallback?**
- Allows offline/partial functionality
- Bridges gap between open signups and admin-controlled creation
- Prevents loss of signup requests

**Why not auto-approve?**
- Security: Admin should review new users
- Control: Prevents spam registrations
- Audit trail: Admin explicitly approves

---

#### `backend/data/db.json`
**Purpose:** Main application database. JSON file containing all persistent data.

**Structure:**
```json
{
  "users": [
    { "id", "email", "fullName", "role", "password", "createdAt" }
  ],
  "tasks": [
    { "id", "title", "description", "assigneeId", "status", "priority", "dueDate", "createdBy", "createdAt", "updatedAt" }
  ],
  "files": [
    { "id", "name", "versions", "contentBase64", "createdAt" }
  ],
  "messages": [
    { "id", "taskId", "userId", "text", "createdAt" }
  ],
  "audit": [
    { "action", "by", "target", "at" }
  ]
}
```

**Why JSON instead of SQL?**
- No schema migrations
- Human-readable
- Easy to version control
- Self-contained (no external database)

**Limitations:**
- Not suitable for production with concurrent users
- No query optimization
- Entire file read/written on each operation
- No transactions

---

## Architectural Decisions & Rationale

### Why This Stack?

| Layer | Technology | Alternative | Why Chosen |
|-------|-----------|------------|-----------|
| Backend Framework | Express.js | Fastify, Hapi, Django | Simplicity, minimal setup, REST-friendly |
| Database | JSON File | PostgreSQL, MongoDB | Self-contained, zero deployment complexity |
| Frontend | Streamlit | React, Vue, Angular | Fast prototyping, built-in components, no build step |
| Authentication | JWT | Sessions, OAuth | Stateless, API-friendly, simple to implement |
| Password Hashing | bcryptjs | crypto, argon2 | Good performance, industry standard |
| ID Generation | nanoid | UUID, auto-increment | URL-safe, shorter, good performance |

### Why Not Microservices?

For a demo project, monolithic architecture is appropriate because:
- Simpler deployment
- Easier debugging
- Fewer moving parts
- Lower operational overhead
- Could migrate to microservices later if needed

### Why Role-Based Access Control (RBAC)?

- Simple and intuitive for small teams
- Covers use case (admin, manager, employee)
- Flexible enough for future expansions
- Could upgrade to attribute-based access (ABAC) if needed

### Why Audit Logs?

- Compliance requirement
- Useful for debugging
- Security posture
- Regulatory requirements
- Could add retention/archival policies

### Frontend vs Backend Separation

**Why separate frontend (Streamlit) from backend (Express)?**
- Clear separation of concerns
- Allows multiple frontends (web, mobile, CLI)
- Backend can be tested independently
- Easier to scale independently
- Supports real API testing with tools like Postman

**Why Streamlit instead of traditional web app?**
- Development speed
- Built-in dashboard components
- No CSS/HTML boilerplate
- Python ecosystem integration
- Ideal for internal tools

---

## Security Considerations

### Current Implementation
- ✅ Password hashing (bcryptjs)
- ✅ JWT token authentication
- ✅ Role-based authorization
- ✅ Audit logging
- ⚠️ No HTTPS (local demo only)
- ⚠️ No token expiration
- ⚠️ No rate limiting
- ⚠️ No input validation (basic examples)
- ⚠️ No CSRF protection (not needed for stateless API)

### Production Improvements
1. Add HTTPS/TLS
2. Implement token expiration and refresh tokens
3. Add rate limiting
4. Input validation and sanitization
5. SQL injection prevention (if using SQL)
6. CORS whitelist specific domains
7. Add helmet.js for security headers
8. Implement 2FA
9. Add password reset flow
10. Encrypt sensitive data at rest

---

## Scalability & Future Improvements

### Current Limitations
1. **Database:** JSON file cannot handle concurrent writes
2. **Storage:** Files stored in memory (limit ~500MB depending on Node.js heap)
3. **Performance:** No caching layer
4. **Realtime:** No WebSocket support
5. **Search:** No full-text search

### Recommended Upgrades
1. **Database:** Migrate to PostgreSQL or MongoDB
   - Command: `npm install sequelize pg` or `npm install mongoose`
   - Benefits: Concurrency, transactions, scaling
   
2. **Caching:** Add Redis
   - Command: `npm install redis`
   - Benefits: Faster queries, session storage
   
3. **File Storage:** Use S3 or Azure Blob
   - Command: `npm install aws-sdk` or `npm install @azure/storage-blob`
   - Benefits: Unlimited storage, CDN integration
   
4. **Realtime:** Add Socket.IO
   - Command: `npm install socket.io`
   - Benefits: Live updates, notifications
   
5. **Search:** Add Elasticsearch
   - Benefits: Fast full-text search, analytics

---

## Running the Project

### Development Setup

**Prerequisites:**
- Node.js (v14+)
- Python (v3.8+)
- npm

**Backend:**
```bash
cd backend
npm install
npm run seed
npm start
```

**Frontend (new terminal):**
```bash
cd ..
pip install streamlit requests pandas
streamlit run app.py
```

### Environment Variables
Create `.env` in `backend/` directory:
```
PORT=4000
JWT_SECRET=your-secret-key-here
NODE_ENV=development
```

### Docker Deployment
To containerize the app, create `Dockerfile`:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY backend/ ./backend/
COPY app.py .
RUN cd backend && npm install
EXPOSE 4000
CMD ["node", "backend/server.js"]
```

---

## File Organization Best Practices Used

1. **Separation of Concerns**
   - `auth.js` - only authentication logic
   - `db.js` - only data persistence
   - `routes/*.js` - only route handlers

2. **Consistent Structure**
   - All routes follow same pattern
   - All middleware uses same signature
   - All error handling consistent

3. **Modular Design**
   - Easy to swap out database layer
   - Easy to add new routes
   - Easy to change authentication method

4. **Clear Naming**
   - Filenames describe content
   - Functions have clear purpose
   - Variables are descriptive

---

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid credentials or token expired | Re-login or reseed database |
| 403 Forbidden | Insufficient permissions | Check user role and endpoint requirements |
| 404 Not Found | Wrong endpoint URL | Verify endpoint path in `routes/*.js` |
| Connection refused | Backend not running | Start backend with `node server.js` |
| Port already in use | Another process on port 4000 | Kill process or change PORT env var |
| ModuleNotFound | Dependencies not installed | Run `npm install` and `pip install streamlit requests pandas` |

---

## Conclusion

This project demonstrates a modern, practical approach to building a task management system with clear separation of concerns, role-based security, and a user-friendly interface. The architecture prioritizes simplicity and speed for demos while remaining scalable and maintainable for future enhancements.

The choice of technologies (Node.js, Express, Streamlit, JWT, JSON) reflects a balance between functionality, complexity, and development speed—ideal for a proof-of-concept or internal tool.

For production deployment, consider the recommended upgrades in scalability section and implement the production security improvements outlined above.
