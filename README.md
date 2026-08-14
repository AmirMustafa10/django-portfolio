# Django Portfolio

A professional developer portfolio platform built with Django, designed to allow developers to showcase their professional profiles, skills, projects, experience, education, and blog content.

The platform also allows users to discover developers and communicate with them through the contact system.

The project follows clean architecture principles, Django best practices, and a professional Git workflow.

---

# Project Goals

- Build a scalable Django application.
- Follow clean architecture principles.
- Apply Django best practices.
- Build reusable and maintainable components.
- Practice professional Git workflows.
- Write clean, maintainable, and well-documented code.
- Provide a platform for developers to showcase their professional profiles and work.

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

### Authentication

- Custom User Authentication
  - User registration
  - Login with username or email

### Developer Profiles

- Developer profiles
- Developer listing
- Developer details
- Profile editing
- Featured developers on the homepage
- Skills management
- Experience management
- Education management

### Portfolio

- Portfolio projects
- Project status management
- Featured projects
- Project gallery
- Project images
- Project skills

### Blog

- Blog posts
- Blog post listing
- Blog post details
- Blog post creation
- Blog post editing
- Blog post deletion
- Blog post comments
- Comment creation
- Comment editing
- Comment deletion
- Comment replies
- Blog post status management

### Contact

- Contact messages
- Message status management

---

## Planned

- Developer search and filtering
- Advanced developer discovery
- Project search and filtering
- Improved user-to-developer communication
- Blog improvements
- Notifications
- API development
- Expanded automated testing

---

# Project Status

🚧 **In Development**

The core architecture, authentication, developer profiles, portfolio management, blog system, and contact functionality are currently implemented.

## Progress

### Core

- [x] Requirements Analysis
- [x] Database Design
- [x] ER Diagram
- [x] Django Project Setup
- [x] Shared Abstract Models

### Accounts

- [x] Accounts application created
- [x] Custom User
- [x] Profile
- [x] Registration form
- [x] Login form
- [x] Email or username login
- [x] Login page
- [x] Registration page
- [x] Homepage
- [x] Developers page
- [x] Developer details page
- [x] Developer Profile editing

### Portfolio

- [x] Portfolio application created
- [x] Skill
- [x] Project
  - [x] Project listing
  - [x] Project details
  - [x] Create project
  - [x] Update project
  - [x] Delete project
- [x] ProjectImage
  - [x] Project image management
  - [x] Image captions
  - [x] Image deletion confirmation
- [x] Experience
  - [x] Create
  - [x] Update
  - [x] Delete
- [x] Education
  - [x] Create
  - [x] Update
  - [x] Delete

### Blog

- [x] Blog application created
- [x] BlogPost
  - [x] Blog listing
  - [x] Blog details
  - [x] Create blog post
  - [x] Update blog post
  - [x] Delete blog post
- [x] Comment
  - [x] Create comment
  - [x] Update comment
  - [x] Delete comment
  - [x] Comment replies

### Contact

- [x] Contact application created
- [x] Message

---

# Project Architecture

## Applications

### Accounts

Responsible for:

- Authentication
- User management
- Registration and login
- Developer profiles
- Developer listing
- Developer details

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

Responsible for:

- Contact messages
- Message management

---

# Project Structure

```text
django-portfolio/
├── accounts/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── portfolio/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   └── ...
│
├── blog/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   └── ...
│
├── contact/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   └── ...
│
├── core/
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── static/
├── templates/
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

---

# Models Overview

## Shared Abstract Models

### TimeStampedModel

Reusable abstract base model providing automatic timestamps.

**Attributes**

- `created_at`
- `updated_at`

---

# Accounts

## User

Custom user model extending Django's `AbstractUser`.

---

## Profile

Represents a developer's professional profile.

**Features**

- One-to-One relationship with `User`
- Avatar upload
- Resume upload
- GitHub link
- LinkedIn link
- Personal website
- Location
- Availability status
- Business validation for "Open to Work"

---

# Portfolio

## Skill

Stores reusable developer skills.

---

## Project

Represents a portfolio project.

**Features**

- SEO-friendly slugs
- Project status management
- Live demo and source code links
- Featured project support
- Many-to-Many relationship with skills

**Key Fields**

- `profile`
- `title`
- `slug`
- `description`
- `status`
- `live_demo_url`
- `source_code_url`
- `is_featured`
- `skills`

---

## ProjectImage

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

## Experience

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

## Education

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

# Blog

## BlogPost

Represents a blog post published by a developer.

**Features**

- Blog post content management
- SEO-friendly slugs
- Publication status management
- Publication date tracking
- Cover image support

**Key Fields**

- `profile`
- `title`
- `slug`
- `content`
- `cover_image`
- `status`
- `published_at`

---

## Comment

Represents a comment submitted on a blog post.

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

# Contact

## Message

Represents a message submitted through the contact form.

**Features**

- Stores contact inquiries
- Tracks sender information
- Supports message status management
- Timestamp tracking

**Key Fields**

- `name`
- `email`
- `subject`
- `status`

---

# Django Admin

## Accounts

### User

- Customized Django Admin interface
- User search and filtering
- Custom user creation fields

### Profile

- Search by username and location
- Filter profiles by availability
- Optimized queries using `list_select_related`
- Organized field groups

---

## Portfolio

### Project

- Customized Django Admin interface
- Search by project title and owner
- Filter by project status and featured flag
- Optimized queries using `list_select_related`
- Improved Many-to-Many editing with `filter_horizontal`
- ProjectImage inline management

### Experience

- Customized Django Admin interface
- Search and filtering for experience records
- Organized experience fields

### Education

- Customized Django Admin interface
- Search and filtering for education records
- Organized education fields

---

## Blog

### BlogPost

- Customized Django Admin interface
- Organized blog post fields
- Search and filtering support

### Comment

- Customized Django Admin interface
- Search and filtering support
- Organized comment fields

---

## Contact

### Message

- Customized Django Admin interface
- Search and filtering support
- Organized message fields

---

# Testing

## Accounts

- ✅ User creation
- ✅ Profile creation
- ✅ File upload validation
- ✅ Business rule validation
- ✅ Django Admin
- ✅ Search and filtering

## Portfolio

- ✅ Skill model

> Additional model and feature tests will be added as development progresses.

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/AmirMustafa10/django-portfolio.git
cd django-portfolio
```

## Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Apply Migrations

```bash
python manage.py migrate
```

## Run the Development Server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

---

# Environment Variables

Create a `.env` file for environment-specific configuration.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

Additional environment variables may be required depending on the database and email configuration.

---

# Git Workflow

The project follows a professional Git workflow:

- Feature branches for new functionality
- Small and focused commits
- Conventional Commit messages
- Separate documentation commits
- Pull Requests for feature integration

### Example Branch

```text
feature/developer-details
```

### Example Commit

```text
feat(developers): add developer details page
```

---

# License

MIT License
