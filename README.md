# Wiki API

A Django REST Framework API for wiki pages with full CRUD, revision history, and revision restore — with per-user authentication and ownership permissions.

## Features

- Create, read, update, and delete wiki pages
- Every edit automatically saves a revision snapshot of the previous content
- Restore any past revision back to being the live content
- Only a page's owner can edit, delete, or restore it — anyone can read

## Requirements

- Python 3.14+
- pip

## Setup

1. **Clone the repo**

git clone https://github.com/yourusername/wiki-api.git
cd wiki-api


2. **Create and activate a virtual environment**

python -m venv venv

   Windows (PowerShell):

venv\Scripts\Activate.ps1

   Mac/Linux:

source venv/bin/activate


3. **Install dependencies**

python -m pip install --upgrade pip
python -m pip install django djangorestframework


4. **Run migrations**

python manage.py migrate


5. **Create a superuser** (for logging into `/admin/` and testing write access)

python manage.py createsuperuser


6. **Run the server**

python manage.py runserver

   Visit `http://127.0.0.1:8000/api/pages/` to see the API.

## Running Tests

python manage.py test


## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/pages/` | List all pages |
| POST | `/api/pages/` | Create a page (auth required) |
| GET | `/api/pages/{id}/` | Retrieve a single page |
| PATCH/PUT | `/api/pages/{id}/` | Update a page (owner only) |
| DELETE | `/api/pages/{id}/` | Delete a page (owner only) |
| GET | `/api/pages/{id}/revisions/` | List a page's revision history |
| POST | `/api/pages/{id}/revisions/{revision_id}/restore/` | Restore a past revision (owner only) |

## Permissions

- Reading pages is open to anyone.
- Creating, editing, deleting, and restoring require being logged in **and** being the page's owner.
- Attempting to write to a page you don't own returns `403 Forbidden`.

Save that as README.md in the project root, then:

git add README.md
git commit -m "Add README"
git push
