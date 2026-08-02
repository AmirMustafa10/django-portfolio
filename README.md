# Django Portfolio

A professional portfolio web application built with Django following clean architecture, scalable architecture, and backend development best practices.

---

# Project Goals

- Build a scalable Django application.
- Follow Clean Architecture principles.
- Apply Django best practices.
- Practice professional Git workflows.
- Write clean, maintainable, and well-documented code.

---

# Tech Stack

- Python
- Django
- PostgreSQL
- HTML
- CSS
- JavaScript
- Bootstrap

---

# Features

## Implemented

- Custom User Authentication
- Developer Profile
- Skills Management

## Planned

- Portfolio Projects
- Project Gallery
- Experience
- Education
- Blog System
- Comments
- Contact Form

---

# Project Status

🚧 **In Development**

## Progress

- [x] Requirements Analysis
- [x] Database Design
- [x] ER Diagram
- [x] Django Project Setup

### Accounts

- [x] Accounts application created
- [x] Custom User
- [x] Profile

### Portfolio

- [x] Portfolio application created
- [x] Skill

### Upcoming

- [x] Project
- [ ] Experience
- [ ] Education
- [ ] Blog
- [ ] Contact

---

# Project Architecture

## Applications

### Accounts

Responsible for:

- Authentication
- User management
- Developer profile

### Portfolio

Responsible for:

- Skills
- Projects
- Project gallery

### Blog

Responsible for blog articles.

### Contact

Responsible for contact messages.

---

# Models Overview

## Shared Abstract Models

### TimeStampedModel

Reusable abstract base model providing automatic timestamps.

**Attributes**

- `created_at`
- `updated_at`

---

## Accounts

### User

Custom user model extending Django's `AbstractUser`.

### Profile

- One-to-One relationship with `User`
- Avatar upload
- Resume upload
- GitHub link
- LinkedIn link
- Personal website
- Availability status
- Business validation for "Open to Work"

---

## Portfolio

### Skill

Stores reusable developer skills.

### Project

Represents a portfolio project.

**Features**

- SEO-friendly slugs
- Project status management
- Live demo and source code links
- Featured project support
- Many-to-Many relationship with skills

**Key Fields**

- `profile`
- `skills`
- `title`
- `description`
- `slug`
- `status`
- `live_demo_url`
- `source_code_url`
- `is_featured`

### Project Image

> Coming soon.

---

## Blog

> Coming soon.

---

# Django Admin

## Accounts

### User

- Customized admin interface

### Profile

- Search by username and location
- Filter by availability
- Optimized queries using `list_select_related`
- Organized field groups

## Portfolio

### Project Admin

- Customized Django Admin interface.
- Search by project title and owner.
- Filter by project status and featured flag.
- Optimized queries using `list_select_related`.
- Improved Many-to-Many editing with `filter_horizontal`.
---

# Testing

## Accounts

- ✅ User creation
- ✅ Profile creation
- ✅ File upload validation
- ✅ Business rule validation
- ✅ Django Admin
- ✅ Search & Filtering

## Portfolio

- ✅ Skill model

---

# Installation

```bash
git clone <repository-url>

cd django-portfolio

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

---

# License

MIT License