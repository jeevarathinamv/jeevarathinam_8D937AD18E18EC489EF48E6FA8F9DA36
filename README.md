# College Admission Seat Allocation System

A simple, modern, and responsive **MCA Project** developed using Python Flask, MySQL / PyMySQL, HTML, CSS, Bootstrap 5, and Jinja2.

## Features

- **Dashboard**: Displays high-level cards for total students, allocated, admitted, waiting, total vacancy, boys, and girls, along with category-wise statistics.
- **Automatic Seat Allocation**:
  - Sorts candidates by Rank Number (ascending) and Marks (descending).
  - Checks candidate's community seat availability first.
  - If community seats are filled, falls back to Open Competition (OC).
  - If both community and OC are full, candidate status is set to `Waiting`.
  - Automatically recalculates allocations whenever a student is added, edited, deleted, or when seat settings are changed.
- **Student Management**: Add, view, edit, search, filter (by Category, Gender, Status), and delete student applications.
- **Admission**: Dedicated admission page showing category-wise seats, allocated, admitted, and vacancies (`Vacancy = Allocated - Admitted`), with single-click student admission processing.
- **Boys & Girls Statistics**: Displays category-wise allocations, admitted candidates, vacancies, and total gender counts.
- **Seat Settings**: Admin can update category-wise seat reservations, triggering immediate automatic recalculation of seat allocations.

## Default Seat Reservations (Total 30 Seats)

- **OC**: 9
- **BC**: 8
- **BCM**: 1
- **MBC**: 6
- **SC**: 5
- **SCA**: 1

## Database Setup

Import `database.sql` into MySQL (or XAMPP phpMyAdmin):

```sql
mysql -u root -p < database.sql
```

Default database configuration:
- Database Name: `college_admission`
- Connection URI: `mysql+pymysql://root:@localhost/college_admission`

## Installation & Running

1. Install dependencies:
   ```bash
   pip install Flask PyMySQL Flask-SQLAlchemy
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open in browser:
   ```text
   http://127.0.0.1:5000
   ```

To run with SQLite fallback for local testing without a MySQL server:
```bash
USE_SQLITE=1 python app.py
```
