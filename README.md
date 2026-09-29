# OpenBooks

OpenBooks is a web platform for publishing and reading books. Users can submit books that can be legally shared, provide the corresponding license or rights information, and send them through a moderation workflow before publication.

The project was developed as the final project for **CS50's Web Programming with Python and JavaScript**.

---

## Distinctiveness and Complexity

OpenBooks is different from the other projects in the course because it is not centered on a conventional CRUD application, social network, or store. It models a small publishing platform with several interconnected workflows: book submission, licensing information, moderation, public reading, ratings, reports, notifications, file handling, and access control.

A submitted book is not immediately public. It starts as `PENDING` and must be reviewed before becoming available. Reviewers can approve or reject submissions, while users can report books that are already public. A reported book is removed from the public catalog until a reviewer resolves the report. This makes the application's behavior depend on the current state of each book and the permissions of the current user.

OpenBooks also goes beyond simply storing uploaded files. PDF books can be read inside the application, EPUB books are rendered with `epub.js`, and Pillow is used to generate a placeholder cover when a book has no cover. Uploaded files are validated and handled according to the book's state and permissions.

The final architecture was the result of an important design decision during development. The project initially explored a more API-centered architecture, but that approach introduced unnecessary frontend complexity for the requirements of the application. The final version therefore uses Django as the core of the application, with server-rendered templates and JavaScript for specific interactive features.

I deliberately kept **Django REST Framework** even though it is not strictly necessary for OpenBooks. I wanted to use the project to practice API development and to build something closer to the way I would approach a larger Django application outside the course. DRF is used selectively for ratings, reports, and moderation data rather than replacing Django's normal views and templates.

Before developing the project, I studied **William S. Vincent's *Django for Professionals* and *Django for APIs***. That additional study influenced several implementation decisions, especially the use of class-based views, the custom user/authentication design, Django's generic views and ORM, and Django REST Framework. I intentionally used these techniques to expand beyond the material directly taught in CS50 Web and to make the project closer to real-world Django development rather than limiting it to the simplest course examples.

The project does not try to maximize complexity. The goal was to choose more advanced tools when they provided a useful solution and to keep simpler Django patterns where they were more appropriate.

---

## Main Features

### Book publication

Users can upload PDF and EPUB files. Each book contains information such as:

* title and author;
* description;
* cover;
* license type;
* uploaded file;
* publication status;
* moderation information.

The application validates uploaded files and associates each book with its uploader.

### Licensing and rights

Books are categorized according to how they may be shared:

* Public Domain;
* Creative Commons;
* Original Work.

Different categories require different information. For example, Creative Commons books require license details, while original works require a declaration of rights.

### Moderation

Books follow this general workflow:

```
PENDING
   |
   +---- APPROVED ----> Public
   |
   +---- REJECTED
```

Reviewers can approve or reject pending books. The application records the reviewer, review time, and reviewer comment.

### Reports

Users can report public books.

When a report is created:

```
APPROVED
    |
    v
REPORTED
    |
    v
Reviewer decision
```

The book is removed from the public catalog until the report is reviewed.

The `Report` model can represent multiple reports, but the current workflow allows only one active report at a time because a reported book immediately leaves the public catalog. This keeps the moderation process and frontend simple while leaving room for future features such as report history or multiple report types.

### Ratings

A user can submit one rating per book. A rating consists of a score and a comment.

The current version intentionally does not include rating editing or deletion. This keeps the feature focused and avoids introducing additional ownership and moderation workflows that are outside the scope of this version.

The database enforces the one-rating-per-user-per-book rule.

The model structure also leaves room for future functionality such as editing ratings, deleting ratings, or allowing authors to respond to comments.

### Reading

Users can read books inside OpenBooks rather than only downloading them.

* PDF files are displayed in the browser.
* EPUB files are rendered using `epub.js`.

### Notifications

Users receive notifications related to moderation activity, including decisions involving books and reports. Notifications can be marked as read and deleted by their owner.

### Search and progressive loading

The application supports searching by title and author. Book lists use Django pagination and JavaScript to load additional results without reloading the entire page.

---

## User Roles and Access

OpenBooks uses a custom user model with reader and reviewer roles. Staff users are also treated as reviewers for moderation purposes.

In general:

* **Readers** can browse and read approved books, rate them, and report public books.
* **Reviewers** can review submissions and reported books.
* **Staff** users have access to Django administration and reviewer capabilities.

Book visibility also depends on state. Approved books are public, while pending, rejected, or reported books are accessible only where the application's permissions allow it.

---

## Architecture and Design Decisions

### Django as the application core

Django handles most of the application:

* authentication;
* authorization;
* forms;
* HTML rendering;
* file handling;
* book moderation;
* reading access.

This keeps the application relatively simple while still allowing JavaScript and API endpoints where they provide a clear benefit.

### Class-based views

The project uses Django class-based views for conventional list, detail, creation, and template-driven functionality. Function-based views are used where a sequence of actions is easier to express procedurally, especially in moderation workflows.

The use of class-based views was strongly influenced by my study of Vincent's Django books before and during the project.

### Django REST Framework

DRF is used selectively for:

* ratings;
* reports;
* reported-book data used by the moderation interface.

It was deliberately included even though OpenBooks could have been implemented without it. This was both a technical and learning decision: I wanted practical experience integrating APIs into a Django application without turning the entire project into an API-driven frontend.

### JavaScript

JavaScript is used only where asynchronous interaction improves the application, including:

* loading more books;
* submitting ratings;
* reporting books;
* notifications;
* moderation tabs;
* conditional fields in the upload form.

The rest of the application remains server-rendered by Django.

---

## Design Decisions About the Data Model

Some models intentionally support more possibilities than the current interface exposes.

For example, the `Report` model can represent multiple reports for a book, while the current workflow allows only one active report at a time. The model therefore remains flexible without making the current moderation interface unnecessarily complicated.

The same principle applies to ratings. The current interface provides one score and one comment per user and does not expose editing or deletion. However, the relationship between users, books, and ratings leaves room for those features in a future version.

These decisions allowed the current frontend to remain manageable while keeping the underlying model extensible.

---

## File Structure

Only the main files created for the application's functionality are listed below.

### `final_project/`

* **`settings.py`** — Django project configuration, installed applications, authentication, database, static and media files, and other project settings.
* **`urls.py`** — Root URL configuration.

### `accounts/`

* **`models.py`** — Custom user model and role-related logic.
* **`forms.py`** — Registration and user-management forms.
* **`views.py`** — Registration and profile views.
* **`urls.py`** — Authentication and profile routes.
* **`admin.py`** — Django administration configuration for the custom user.

### `books/`

* **`models.py`** — Book, rating, and report models, validation, status/license choices, access control, and database constraints.
* **`views.py`** — Book listing, search, detail, upload, reading, ratings, reports, and moderation views, including the DRF endpoints.
* **`serializers.py`** — DRF serializers for ratings, reports, and moderation data.
* **`urls.py`** — Routes for the books application.
* **`covers.py`** — Placeholder-cover generation using Pillow.
* **`templatetags/book_tags.py`** — Custom template filter for displaying ratings as stars.
* **`tests/`** — Tests for book models, validation, permissions, ratings, reports, and views.

### `home/`

* **`views.py`** — Home-page data and platform statistics.
* **`urls.py`** — Home-page route.

### `notifications/`

* **`models.py`** — Notification model.
* **`views.py`** — Notification listing, read-state management, and deletion.
* **`urls.py`** — Notification routes.
* **`admin.py`** — Django administration configuration.

### `templates/`

Contains the server-rendered HTML interface for the home page, authentication, profiles, books, moderation, reading, and notifications.

### `static/`

Contains the application's CSS and JavaScript. The main JavaScript files handle book-list loading, ratings and reports, upload-form behavior, notifications, and moderation.

### `media/`

Contains uploaded book files and generated covers used by the application.

---

## Technologies

* Python
* Django
* Django REST Framework
* JavaScript
* HTML/CSS
* Bootstrap
* SQLite
* Pillow
* `epub.js`

---

## Testing

The project includes Django tests covering the main rules of the application, including:

* book states and visibility;
* user permissions;
* license validation;
* uploaded-file validation;
* rating constraints;
* reports;
* moderation behavior;
* view access.

Run the tests with:

```
python manage.py test
```

---

## Installation and Setup

### 1. Clone the repository

```
git clone https://github.com/LeodanyPM/OpenBooks.git
cd OpenBooks
```

### 2. Create a virtual environment

Linux/macOS:

```
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Apply migrations

```
python manage.py migrate
```

### 5. Create an administrative user

```
python manage.py createsuperuser
```

A staff user can access Django administration and is also treated as a reviewer by OpenBooks.

### 6. Run the server

```
python manage.py runserver
```

---

## External Learning and References

The project was developed using CS50 Web as the primary course material, supplemented by independent study of:

* William S. Vincent, *Django for Professionals*
* William S. Vincent, *Django for APIs*

These books were particularly influential in my use of class-based views, custom authentication patterns, Django's ORM and generic views, and Django REST Framework.

I used this additional study to go beyond the techniques explicitly presented in the course and to make deliberate implementation choices based on broader Django development practices.

---

## Scope and Future Possibilities

The current version intentionally focuses on the core publishing, reading, rating, reporting, and moderation workflows.

Features that could be added in future versions include:

* editing or deleting ratings;
* author replies to rating comments;
* more detailed report histories;
* multiple report types;
* additional moderation functionality.

The existing models were designed to leave room for these extensions without making the current version unnecessarily complex.

---

## Final Notes

OpenBooks was developed iteratively. The architecture changed during development as I gained a better understanding of the complexity of a SPA-oriented approach. The final design therefore deliberately uses Django as the core, JavaScript for targeted interactivity, and Django REST Framework where an API provides a useful benefit.

The project reflects both the material learned in CS50 Web and additional Django study. The main objective was not to use as many technologies as possible, but to build a coherent application while making deliberate decisions about architecture, permissions, data modeling, and future extensibility.
