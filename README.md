# Homeschool Hub - Elementary Education Management System

A comprehensive web application designed for elementary homeschooling management, featuring student tracking, assignment management, grade recording, and detailed progress analytics.

## Features

### 🎓 Student Management
- Add and manage multiple students
- Track individual student progress
- Maintain student profiles and information

### 📚 Assignment & Grade Tracking
- Create and manage assignments across subjects
- Record grades and track completion
- Set due dates and monitor overdue assignments

### 📊 Progress Analytics
- Interactive charts showing grade trends over time
- Subject performance analysis with pie and bar charts
- Attendance tracking with visual reports
- Student comparison analytics
- AI-powered insights and recommendations

### 🎯 Subject Management
- Organize curriculum by subjects
- Track time allocation across different subjects
- Monitor performance vs learning goals

### 📈 Data Visualization
- Line charts for grade progress tracking
- Pie charts for subject distribution
- Bar charts for performance comparisons
- Area charts for attendance patterns
- Export functionality for reports

## Technology Stack

- **Frontend**: React 18, Vite, TailwindCSS, Shadcn/UI, Recharts
- **Backend**: Flask, SQLAlchemy, Flask-CORS
- **Database**: PostgreSQL (production) / SQLite (development)
- **Containerization**: Docker, Docker Compose
- **Deployment**: Ready for Portainer and container orchestration

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Portainer (optional, for container management)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd homeschool-hub
cp .env.example .env
```

### 2. Configure Environment
Edit the `.env` file with your settings:
```env
DB_PASSWORD=your_secure_password
APP_PORT=3256
SECRET_KEY=734a6aca97e252e46973241d80e4eda4c6d626e91f9c019442951be6e60eb1e2
JWT_SECRET_KEY=233ce7b87d1c5af4a930c2f701bdb69eec6ec94bb3beb537c3ed36d5e1e7d546
CORS_ORIGINS=http://localhost:3000
```

### 3. Deploy with Docker Compose
```bash
docker-compose up -d
```

The application will be available at `http://localhost:3256`

### 4. Access the Application
- Open your browser to `http://localhost:3256`
- Create your first teacher account
- Start adding students and assignments

## Portainer Deployment

### Using Portainer Stacks
1. In Portainer, go to **Stacks** → **Add Stack**
2. Name your stack: `homeschool-hub`
3. Copy the contents of `docker-compose.yml`
4. Set environment variables in the Portainer interface:
   - `DB_PASSWORD`: Your database password
   - `APP_PORT`: Port to expose (default: 3256)
   - `SECRET_KEY`: Application secret key (32+ chars)
   - `JWT_SECRET_KEY`: JWT secret key
   - `CORS_ORIGINS`: Allowed CORS origins
5. Deploy the stack

### Using Portainer App Templates
1. Create a custom app template with the docker-compose.yml
2. Deploy from the template with your environment variables

## Manual Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (optional, SQLite used by default)

### Backend Setup
```bash
cd homeschool-hub
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd src && python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables
- `DB_PASSWORD`: Database password for PostgreSQL
- `APP_PORT`: Port for the application (default: 3256)
- `SECRET_KEY`: Flask secret key for sessions (32+ chars)
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins
- `DATABASE_URL`: Full database connection string
- `FLASK_ENV`: Environment (production/development)
- `MAX_CONTENT_LENGTH`: Maximum file upload size

### Database Configuration
The application supports both PostgreSQL (recommended for production) and SQLite (development):

**PostgreSQL** (Production):
```env
DATABASE_URL=postgresql://username:password@host:port/database
```

**SQLite** (Development):
```env
# Leave DATABASE_URL unset, SQLite will be used automatically
```

## Features Overview

### Dashboard
- Overview of total students, assignments, and completion rates
- Recent assignments and student progress
- Quick action buttons for common tasks

### Student Management
- Add/edit student information
- Track individual student progress
- View student-specific analytics

### Assignment Tracking
- Create assignments with due dates
- Track completion status
- Grade assignments and provide feedback

### Progress Analytics
- **Grade Trends**: Line charts showing improvement over time
- **Subject Analysis**: Pie charts for time distribution, bar charts for performance vs goals
- **Attendance Tracking**: Area charts showing attendance patterns
- **Student Comparison**: Compare performance across multiple students

### Insights & Recommendations
- AI-powered analysis of student performance
- Automated recommendations for improvement
- Alerts for attendance issues or grade concerns

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Students
- `GET /api/students` - List all students
- `POST /api/students` - Create new student
- `GET /api/students/:id` - Get student details
- `PUT /api/students/:id` - Update student
- `DELETE /api/students/:id` - Delete student

### Assignments
- `GET /api/assignments` - List assignments
- `POST /api/assignments` - Create assignment
- `PUT /api/assignments/:id` - Update assignment
- `DELETE /api/assignments/:id` - Delete assignment

### Grades
- `GET /api/grades` - List grades
- `POST /api/grades` - Record grade
- `PUT /api/grades/:id` - Update grade

### Health Check
- `GET /api/health` - Application health status

## Security Features

- Password hashing with bcrypt
- JWT-based authentication
- CORS protection
- Input validation and sanitization
- Environment-based configuration
- Secure database connections

## Backup and Maintenance

### Database Backup
```bash
# PostgreSQL backup
docker exec homeschool-hub-db pg_dump -U homeschool_user homeschool_hub > backup.sql

# Restore
docker exec -i homeschool-hub-db psql -U homeschool_user homeschool_hub < backup.sql
```

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Troubleshooting

### Common Issues

**Database Connection Issues**:
- Check PostgreSQL container is running: `docker ps`
- Verify environment variables are set correctly
- Check database logs: `docker logs homeschool-hub-db`

**Application Won't Start**:
- Check application logs: `docker logs homeschool-hub-app`
- Verify all required environment variables are set
- Ensure ports are not already in use

**Frontend Not Loading**:
- Verify the frontend was built: check `frontend/dist` directory
- Check if static files are being served correctly
- Clear browser cache

### Health Checks
Visit `http://localhost:3256/api/health` to check application status.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review application logs
- Create an issue in the repository

---

**Built with ❤️ for homeschooling families**

