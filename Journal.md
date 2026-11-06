## Day 1: Environment setup(9 Oct 2026)

What I built:
- I setup the environment
- downloaded all the packages
- activated the (venv) in the terminal
- saved the requierements.txt in the terminal with pip freeze
- wrote .gitignore so private and rebuildable things. stay  out of git
-r un git status to check that nothing private will be uploaded

What confused me:
- i typed the .gitignore rules in the terminal rather than the file itself and was confused by the messages i was getting (that the terminal giving permission denied)

How I fixed it:
- checked online and using AI, turns out had to type them in the .gitignore file itself

What i learned today (reflections)?
### Why does each project need its own virtual environment?

- Every project needs its own isolated environment to prevent conflicts, protect system stability, and make deployment predictable.
- Writing a requirements file makes teamwork easy: everyone can freeze the dependencies and use the same settings to run the code.
- There should always be a planning phase to make work go smoothly:
  - choose the language and the libraries to install
  - decide how the app will be packaged (Docker, Kubernetes, etc.)
  - decide where to host the app (locally, cloud-based, etc.)

### What would go wrong if I committed the venv folder?

- The repo becomes slow and bloated by hundreds of MB.
- The Git history becomes unreadable because of the many changes inside the venv.
- It can break on other operating systems, because it is hard-coded to my machine.
- It can cause problems on everyone else's machine (the team).

### Why is comitting venv pointless?
- The requirements.txt file already records the exact names and versions of a project's dependencies, which makes committing the entire venv (virtual environment) folder completely redundant.

## Mission 1: A home for shifts (6 Nov 2026)
 What I built:
- created database.py to handle the database connection and session setup
- created models.py to define the Shift database table using SQLAlchemy 2.0
- mapped out the table columns: id, venue, shift_date, start_time, end_time, hourly_rate, and notes
- used modern typing like Mapped[str] and mapped_column() to give Python full autocompletion and type checking
- Ran python -c "import models" in the terminal with (venv) active and it printed nothing, confirming there are no syntax errors.
What confused me:
- the difference between the database engine, the session, and the sessionmaker factory
- deciding what data type to use for hourly_rate (Decimal vs float)
How I fixed it:
- used the restaurant analogy to make the database concepts click: the engine is the kitchen road, sessionmaker hires waiters, and the session is your specific waiter taking your order
- switched hourly_rate from Decimal to float after realizing SQLite doesn't natively support Decimal types without extra setup, and that multiplying a float (hours) by a Decimal in Python would throw a TypeError during pay calculations in Mission 5

What I learned today (reflections)?
## Why shouldn't you store calculated values like total pay in the database
- Storing calculated fields like pay creates stale data risks: if you update the hourly_rate later, the stored pay will be wrong unless you remember to manually recalculate and update it
- Computing pay dynamically on the fly (hours * hourly_rate) guarantees the math is always accurate and up to date

## What is the difference between a Model Class and a Database Row
- The model class (Shift) is the blueprint or template that defines the structure and rules of the table (like a blank job application form)
- A database row is an individual object created from that class containing actual data for one specific shift (like a completed form with real values filled in

### Why isn't shift duration (hours) stored as a column?
- Just like total pay, shift duration is a derived value that can be calculated directly from `start_time` and `end_time`
- If you store `hours` separately and someone later updates the `end_time`, the stored `hours` become wrong—computing it dynamically ensures it's always accurate