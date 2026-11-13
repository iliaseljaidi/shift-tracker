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

## Mission 2: Accept a shift, POST (9 Nov 2026)

What I built:
- schemas.py with two Pydantic schemas: ShiftCreate (incoming data) and ShiftOut (outgoing data, adds the id)
- main.py with a POST /shifts endpoint that validates a shift, saves it to SQLite and returns it with status 201
- create_all runs on startup, so the shifts table is built automatically
- Tested it in /docs: a valid shift returned 201 with an id, and I checked the row in shifts.db with sqlite3
- Tested it in /docs: a valid shift returned 201 with an id, and a negative rate returned 422 naming the hourly_rate field
- Restarted the server and checked shifts.db with sqlite3: the row was still there

What confused me:
- I wrote Field(default=0) for hourly_rate, which makes the field optional and lets bad rates through instead of rejecting them
- I used underscore_attrs_are_private in model_config instead of from_attributes
- I could not find "the docs" at first. The /docs page was already open, and I had to click the POST /shifts bar, then Try it out

How I fixed it:
- Changed the rate to Field(gt=0), which makes it required and rejects 0 or negative values
- Changed model_config to ConfigDict(from_attributes=True) so Pydantic can read a SQLAlchemy object
- Learned that the green POST /shifts bar on /docs is where you test the endpoint
## Reflections

- Why is it better to validate input at the edge than inside the database?

Validating at the edge (using Pydantic/FastAPI) catches bad data immediately before it ever hits your application logic or database. It saves database resources, provides clear, human-readable error messages back to the user instantly, and prevents corrupted or invalid data states from ever being stored.

- What does commit do? What happens if you forget it?

commit() tells the database session to permanently save your changes to disk. If you forget it, the transaction remains pending or gets rolled back when the session closes, meaning your changes disappear and the database file won't actually contain the new data.

## Mission 3: Read shifts, GET (13 Nov 2026)

What I built:
- GET /shifts, which returns every shift as a list, newest first, using order_by with desc() on shift_date
- GET /shifts/{shift_id}, which returns one shift by id using a path parameter and db.get
- A 404 with the message "Shift not found" when the id does not exist, raised with HTTPException
- Tested in /docs with shifts posted on jumbled dates: (CONFIRM: newest first? /shifts/999 gave 404?)

What confused me:
- I had to remember how to open /docs and post test shifts again before I could test anything
- (add anything else that tripped you up while writing the endpoints)

How I fixed it (and which hint level I needed):
- Did my research first and answered the check questions: GET is the read method, list[schemas.ShiftOut] is a list response, db.get returns None when nothing matches, and HTTPException takes a status_code and a detail
- Tried to write the endpoints myself first, then asked for the full code and typed it out

One thing I would do differently (Missions 0 to 3):
- Check whether I am in the terminal or the file editor before typing, and read each schema rule carefully (Field(default=0) let bad rates through instead of rejecting them)

Interview story (problem, action, result):
- My API accepted shifts with a rate of 0 because I used Field(default=0) instead of Field(gt=0). I tested a negative rate in /docs, read the 422 error, and fixed the rule, so now invalid rates are rejected before they reach the database.

## Reflections

### Why return 404 instead of an empty object when an id is missing?
- A 404 clearly says that the shift does not exist, whereas an empty object could look like a valid response with missing data or create ambiguity about whether the resource genuinely doesn't exist or if a query filter returned zero results

### What happens to the list endpoint with 100,000 shifts? How might I fix it?
- It would try to return 100,000 records at once, exhausting server memory, creating a massive JSON payload, and slowing down response times, and the fix is pagination using limit and offset query parameters.