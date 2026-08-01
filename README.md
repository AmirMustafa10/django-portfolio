# Django Portfolio

A professional portfolio web application built with Django following clean architecture and backend development best practices.

## Project Goals

- Build a scalable Django application.
- Follow Clean Architecture principles.
- Apply Django best practices.
- Practice Git workflow with professional commits.
- Document the development process.

---

## Features (Planned)

- Custom User Authentication
- Developer Profile
- Skills Management
- Portfolio Projects
- Project Gallery
- Experience
- Education
- Blog System
- Comments
- Contact Form

---

## Project Status

🚧 In Development

### Progress

- [x] Requirements Analysis
- [x] Database Design
- [x] ER Diagram
- [x] Django Project Setup
- [x] Accounts application created
- [x] Custom User
- [x] Profile
- [x] Portfolio application created
- [ ] Blog
- [ ] Contact

---

## Project Structure

- accounts
  - User authentication
  - User profile management

---

### Authentication

- Custom User model based on Django AbstractUser.

## Tech Stack

- Python
- Django
- PostgreSQL
- HTML
- CSS
- JavaScript
- Bootstrap

---

## License

MIT

## Accounts Module

### Models

#### User
- Custom user model extending Django's `AbstractUser`.

#### Profile
- One-to-One relationship with `User`.
- Supports avatar and resume uploads.
- Stores professional links (GitHub, LinkedIn, Website).
- Includes profile availability status.
- Enforces business validation for "Open to Work" profiles.

### Admin

- Customized Django Admin for User and Profile.
- Search by username and location.
- Filter profiles by availability.
- Optimized admin queries using `list_select_related`.
- Field Grouping


## Testing

### Accounts Module

- ✅ User creation
- ✅ Profile creation
- ✅ File upload validation
- ✅ Business rule validation
- ✅ Django Admin
- ✅ Search & Filtering

### Portfolio

#### Skill
Stores reusable developer skills.