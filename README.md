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
- [x] Project
- [x] ProjectImage
- [x] Experience
- [x] Education

### Blog

- [x] Blog application created
- [x] BlogPost
- [x] Comment

### Contact

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
- Experience
- Education

### Blog

Responsible for:

- Blog posts
- Comments

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

---
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

---

### Project Image

Represents images associated with portfolio projects.

**Features**

- Associates images with projects
- Supports multiple images per project
- Stores optional image captions
- Supports custom display ordering

**Key Fields**

- `project`
- `image`
- `caption`
- `display_order`

---
### Experience

Represents a developer's professional work experience.

**Features**

- Supports different employment types
- Stores company and job information
- Tracks employment dates
- Supports current positions

**Key Fields**

- `profile`
- `job_title`
- `company`
- `employment_type`
- `description`
- `start_date`
- `end_date`
- `currently_working`

---

### Education

Represents a developer's educational background.

**Features**

- Stores academic institution information
- Tracks degree and field of study
- Supports education dates

**Key Fields**

- `profile`
- `institution`
- `degree`
- `field_of_study`
- `start_date`
- `end_date`
- `grade`
- `description`

---

---

## Blog

### BlogPost

Represents a blog post published by the developer.

**Features**

- Blog post content management
- SEO-friendly slugs
- Publication status management
- Publication date tracking

**Key Fields**

- `profile`
- `title`
- `slug`
- `content`
- `cover_image`
- `status`
- `published_at`

---

### Comment

Represents comments on blog posts.

**Features**

- Associates comments with blog posts
- Supports author information
- Comment moderation support
- Timestamp tracking

**Key Fields**

- `user`
- `blog_post`
- `content`

---


# Django Admin

## Accounts

### User

- Customized admin interface

---

### Profile

- Search by username and location
- Filter by availability
- Optimized queries using `list_select_related`
- Organized field groups

---

## Portfolio

### Project Admin

- Customized Django Admin interface.
- Search by project title and owner.
- Filter by project status and featured flag.
- Optimized queries using `list_select_related`.
- Improved Many-to-Many editing with `filter_horizontal`.
- ProjectImage inline management
---

### Experience Admin

- Customized Django Admin interface
- Search and filtering for experience records
- Organized experience fields

---

### Education

- Customized Django Admin interface
- Search and filtering for education records
- Organized education fields

---

## BlogPost

### BlogPost

- Customized Django Admin interface
- Organized blog post fields
- Search and filtering support

---

### Comment

- Customized Django Admin interface
- Search and filtering support
- Organized comment fields

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
git clone https://github.com/AmirMustafa10/django-portfolio.git

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
