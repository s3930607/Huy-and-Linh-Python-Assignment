# Huy-and-Linh-Python-Assignment
Python Programming Studio Assignment

# Preventable Infectious Diseases

Studio project web application for COSC3106.

## Running it

First time only:

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python db/setup_db.py

Then, every time:

    .venv\Scripts\activate
    python app.py

Open http://127.0.0.1:5000 in a browser.

`db/setup_db.py` creates the Persona, TeamMember and MissionStatement tables and
fills them with placeholder rows. Replace those placeholders in
`db/seed_data.sql` with your own personas and team details, then run the script
again.

## Pages

| Level | Sub-task A | Sub-task B |
|-------|------------|------------|
| 1 | `/` landing | `/mission` mission statement |
| 2 | `/vaccination-rates` | `/infection-economy` |
| 3 | `/improvement` | `/above-average` |

## Layout

    app.py              creates the Flask app and registers the three blueprints
    config.py           where the database file lives
    database/
      connection.py     opens and closes one connection per query
      queries.py        every SQL statement in the project
    routes/
      __init__.py       guards that check user input against allowed values
      level1.py         landing and mission
      level2.py         the two mid-level pages
      level3.py         the two deep-dive pages
    db/
      immunisation.db   supplied data plus our three added tables
      schema_extension.sql
      seed_data.sql
      setup_db.py
    templates/          one file per page, all extending base.html
    static/css/

## Notes on the data

The `coverage`, `doses` and `target_num` columns are declared REAL but around a
quarter of their rows hold an empty string. SQLite ranks text above every number,
so `coverage >= 90` matches those blank rows. Every query that reads these
columns filters with `typeof(...) = 'real'` first.

Coverage figures above 100% are shown as reported rather than capped: the doses
given exceeded the estimated target group.

493 rows in `Vaccination` name nine small territories that are absent from
`Country`, so an inner join drops them. They have no population figures either.

## This README was studied and modeled after some open-source GitHub community projects.
