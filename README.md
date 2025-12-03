# TaskFlow - Task Management System

A complete task management application built with **Express.js** backend and **Streamlit** frontend.

## Quick Start

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- npm

### Backend Setup

```bash
cd backend
npm install
npm run seed
node server.js
```

Backend runs on: **http://localhost:4000**

### Frontend Setup (New Terminal)

```bash
cd ..
pip install streamlit requests pandas
streamlit run app.py
```

Frontend runs on: **http://localhost:8501**

---

## Features

### Dashboard
- View task statistics
- See task summary by status
- Quick task status updates
- Welcome greeting

### Task Management
- Create, read, update tasks
- Filter by status
- Set priority levels
- View task details
- Mark tasks complete

### File Management
- Upload files
- View uploaded files
- Track file versions
- Download files

### Messages
- Send and receive messages
- View message history
- Real-time updates

### Reports
- Download task reports (CSV/JSON)
- View task statistics
- Status distribution chart
- Priority distribution chart

### Employee Management (Admin Only)
- View all employees
- Add new employees
- Assign roles (Admin, Manager, Employee)
- Default password: `TaskFlow@123`
 - Delete employees (Admin and Manager role restrictions apply)
 - Pending self-signup requests stored locally at `data/pending_signups.json` (Admins can review/approve via the Employees page)

### Audit Logs (Admin Only)
- Track all system actions
- View action history
- User and timestamp information

---

## Demo Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@local | Admin@123 |
| **Manager** | manager@local | Manager@123 |
| **Employee** | employee@local | Employee@123 |

---

## Project Structure

```
workflow-system/
├── backend/
│   ├── server.js                 # Express server
│   ├── db.js                     # Database (JSON file)
│   ├── auth.js                   # Authentication
│   ├── seed.js                   # Initial data seeding
│   ├── package.json
│   └── routes/
│       ├── tasks.js              # Task routes
│       ├── dashboard.js          # Dashboard routes
│       ├── users.js              # User management
│       ├── files.js              # File handling
│       ├── messages.js           # Messages
│       ├── reports.js            # Reports
│       └── audit.js              # Audit logs
│
├── frontend/                     # (React/Vite - deprecated) (removed from repo — Streamlit UI `app.py` is the supported frontend)
│
├── app.py                        # Streamlit main application
├── README.md
└── data/
    └── db.json                   # JSON database
```

---

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login

### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task

### Dashboard
- `GET /api/dashboard/summary` - Get dashboard summary

### Users
- `GET /api/users` - Get all users (admin only)
- `POST /api/users` - Create user (admin only)
- `POST /api/users/signup` - Public employee self-registration
 - `DELETE /api/users/:id` - Delete a user (Admin can delete any user except themselves; Manager can delete users with role `EMPLOYEE`)

### Files
- `GET /api/files` - Get all files
- `POST /api/files` - Upload file
- `GET /api/files/:id` - Get file details

### Messages
- `GET /api/messages` - Get all messages
- `POST /api/messages` - Send message

### Reports
- `GET /api/reports/tasks` - Get task report (supports ?format=csv)

### Audit
- `GET /api/audit` - Get audit logs (admin only)

---

## Tech Stack

### Backend
- **Express.js** - Web framework
- **JWT** - Authentication
- **bcryptjs** - Password hashing
- **nanoid** - ID generation
- **CORS** - Cross-origin support

### Frontend
- **Streamlit** - Web UI framework
- **Requests** - HTTP client
- **Pandas** - Data handling

### Database
- **JSON File** - Simple file-based storage

---

## Usage Examples

### Add a Task
1. Go to **Tasks** > **Create Task**
2. Enter title and description
3. Set priority (1-5)
4. Click "Create Task"

### Upload a File
1. Go to **Files** > **Upload File**
2. Enter filename
3. Select file
4. Click "Upload"

### Manage Employees (Admin)
1. Go to **Employees**
2. Fill in employee details
3. Select role
4. Click "Add Employee"

### View Reports
1. Go to **Reports**
2. Download as CSV or JSON
3. View charts and statistics

---

## Configuration

### Environment Variables (Optional)
```bash
PORT=4000              # Backend port
NODE_ENV=development   # Environment
```

### Default Database Location
```
backend/data/db.json
```

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 4000
lsof -ti:4000 | xargs kill -9

# For Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 4000).OwningProcess | Stop-Process
```

### Module Not Found
```bash
npm install
pip install streamlit requests pandas
```

### API Connection Error
- Ensure backend is running on port 4000
- Check CORS settings in `backend/server.js`
- Verify network connectivity
### Pending Signups and Offline Signup
- If users sign up while the backend is unreachable or public user creation is forbidden, signup requests are saved locally at `data/pending_signups.json`.
- Admins can review and approve or reject these entries from the Streamlit `Employees` page (Approve will create the user with a default password `TaskFlow@123`).

---

## Future Enhancements

- [ ] PostgreSQL/MongoDB integration
- [ ] Email notifications
- [ ] Advanced filtering
- [ ] User profile management
- [ ] Two-factor authentication
- [ ] Real-time updates (WebSocket)
- [ ] Mobile app
- [ ] Dark mode

---

## License

MIT License - Feel free to use this project

---

## Support

For issues or questions, please check the documentation or contact the development team.

Happy Task Management!
