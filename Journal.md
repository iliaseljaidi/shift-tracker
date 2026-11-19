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

## Mission 4: Fix mistakes, PUT and DELETE (14 Nov 2026)

What I built:
- PUT /shifts/{shift_id}, which replaces a shift's data with new data and returns the updated shift
- DELETE /shifts/{shift_id}, which removes a shift and returns 204 with no body
- Both return 404 when the shift id does not exist
- Tested in /docs: (CONFIRM: did a PUT change the rate, and did a GET confirm it? Did GET on a deleted id give 404? Did PUT and DELETE on 999 give 404?)

What confused me:
- When I pasted my code, three extra lines ended up flush left at the bottom of main.py, outside any function. Python runs those when the file loads, so they would have crashed the server on startup
- (add anything else, for example the indentation or how setattr works)

How I fixed it (and which hint level I needed):
- Removed the stray lines so the file ended with db.commit() inside delete_shift
- Wrote the endpoints myself first, then checked them against the expected structure

The line I wrote three times:
- The find-or-404 block (db.get, then if shift is None, raise HTTPException 404) appears in get_shift, update_shift and delete_shift. I will replace it with one helper in Mission 6

## Mission 5: The overnight problem, hours, pay and summaries (15 Nov 2026)

What I built:
- calc.py with shift_hours(), which turns both times into minutes since midnight and adds 24 hours when the end is earlier than the start
- hours and pay as computed fields on the outgoing schema, rounded to 2 decimals and never stored in the database
- GET /summary/weekly, which returns the number of shifts, total hours and total pay for the 7 days from a start date
- Tested it: a 22:00 to 04:00 shift at 14.50 came back as 6 hours and 87.0 pay, and the weekly summary only counted shifts inside the 7 days

What confused me:
- Where the weekly summary code went in main.py. I also forgot that it needed import datetime at the top
- I pasted the word "python" from a code block into my file by mistake, which would have crashed the server

How I fixed it (and which hint level I needed):
- Asked where the function belonged, added the import, and removed the stray word. I asked for the full answer after trying the steps myself first

Decision I made:
- A shift that starts and ends at the same time: 0 hours. If someone puts 09:00 to 09:00, that is either a mistake or a zero-length shift, not someone working a full 24 hours straight. Counting it as 24 hours would inflate pay way too easily.

A mismatch I found later (19 Nov 2026):
- My journal said 0 hours for equal times, but my code counted them as 24, because the condition was end_min <= start_min. Writing it down made me check. I changed <= to <, added test_same_start_and_end, and watched it fail with 24.0 == 0 before the fix. The suite is now 8 tests

One thing I would do differently:
- Read the pasted code block carefully before copying, so labels and stray lines do not end up in the file

### Reflections
- Why is calculating hours safer than storing them?
  - If I store hours in the database and later edit a shift's start or end time, the stored hours can easily go out of sync. Calculating them from the start and end times means there is only one source of truth and I don't store duplicate data.
- What bugs might appear when the clocks change at 01:00 or 02:00 in spring or autumn? (I only had to notice this, not fix it)
  - Because shift_hours() only looks at raw clock times and doesn't know about timezones or daylight saving, a spring clock change would add an extra hour by mistake (overcounting by 1 hour) and an autumn clock change would lose an hour (undercounting by 1 hour).

## Mission 6: Lock it down, login and privacy (16 Nov 2026)

What I built:
- 6a: a User table (id, unique email, password_hash) and a user_id foreign key on Shift. I deleted shifts.db once so create_all could rebuild the tables
- 6b: auth.py with hash_password, verify_password and create_token (2 hour expiry), plus POST /register and POST /login
- 6c: get_current_user, which reads the token, decodes it, loads the user and returns 401 if anything fails. Every shift endpoint and the weekly summary now depends on it
- A get_own_shift helper that replaced the find-or-404 block I had written three times. It returns 404 when a shift is missing or belongs to someone else
- create_shift sets user_id from the logged-in user, and list and summary queries filter by user_id
- SECRET_KEY is read from an environment variable with os.getenv, with a development-only fallback

What confused me:
- The login form calls the email field "username". That is part of the OAuth2 standard, so I put my email in it
- Why shifts.db had to be deleted: create_all only builds missing tables and never changes an existing one, so the old shifts table had no user_id column

How I tested it:
- Registering twice with the same email gave 400, a short password gave 422, a wrong password and an unknown email both gave 401 with the same message, and a right password gave a token
- The database stores an argon2 hash, never the real password
- Without a token, GET /shifts gave 401
- I also had Claude Code run 13 checks with curl, and all passed. It pointed out that they could not prove privacy yet, because only one user's data existed
- The attack: I registered a second account (B) and tried to use account A's shift. B's GET /shifts returned an empty list, and GET, PUT and DELETE on A's shift id all gave 404. A's shift was unchanged in the database afterwards (still Test Bar at 14.5)
- In the same week as A's 6 hour shift, B's weekly summary counted only B's own shift (1 shift, 5.0 hours, 50.0 pay)

Things I noticed:
- A 422 validation error echoes the submitted password in its input field. FastAPI does this by default, and I want to look up how to hide it
- My test accounts and shifts stay in shifts.db, which is why Mission 7 uses a temporary database

One thing I would do differently:
- Test with two accounts from the start. One user's data cannot show whether privacy works

### Reflections
- Why is 404 better than 403 when someone requests another user's shift?
  - 403 tells an attacker that the shift exists even though they aren't allowed to see it. 404 doesn't give away whether that shift ID exists at all.
- What would an attacker gain if they stole the SECRET_KEY?
  - They could sign their own tokens for any user ID without needing a password, so they could act as any user and read or change their shifts.
- If a token is stolen, what limits the damage? What would a real production system add?
  - The 2-hour expiry limits how long a stolen token works. In a real production system I'd use shorter-lived access tokens with refresh tokens, a way to revoke tokens, and safer storage like HTTP-only cookies over HTTPS.

## Mission 7: Prove it works, automated tests (17 Nov 2026)

What I built:
- Unit tests for shift_hours (normal, overnight and half-hour shifts)
- API tests that use a temporary in-memory SQLite database (StaticPool) swapped in with app.dependency_overrides, so they never touch shifts.db
- An autouse fixture that drops and recreates all tables before every test
- A create_auth_header helper that registers, logs in and returns the Authorization header
- Tests for create and list, login required (401), negative rate rejected (422), and a two-user security test. 7 tests in total, all passing

What confused me:
- Python import syntax. I wrote "import X from Y", but Python needs "from Y import X"
- The yield in a fixture. Everything before it runs before the test and everything after it runs after, so my first version dropped the tables and then built them too late
- pytest ran only 3 tests because I had named the file tests_api.py. It only collects files starting with test_, and it gave no error
- My first security assert compared B's list to a list that contained the 404 response, so it was checking the wrong thing. It needed to check that B's list is empty
- An IndentationError when I commented out the only line inside an if, and "None == 8" failures when the return line ended up in the wrong place

How I fixed it (and which hint level I needed):
- Renamed the file to test_api.py, removed the yield, and changed the assert to == []

Breaking it on purpose:
- Changing the overnight rule to end_min += 0 made the overnight shift test fail
- Removing the user_id filter made the security test fail, because B's list contained A's shift. My first version of that test would not have caught it
- Changing Field(gt=0) to Field(default=0) made test_negative_rate_rejected fail, because a negative rate was accepted with 201 instead of 422
- Checking user and shift counts in shifts.db before and after pytest showed they did not change (3 and 3)

Things I noticed:
- InsecureKeyLengthWarning: my fallback SECRET_KEY is only 18 bytes, and PyJWT recommends 32 or more
- A deprecation warning about httpx and the Starlette TestClient

One thing I would do differently:
- Check that pytest is collecting every test file (python -m pytest -v) before assuming all my tests ran

### Reflections
- Which test would catch the bug I am most afraid of? Did I write it?
  - test_users_cannot_see_each_others_shifts. Leaking one person's shifts or pay to another user would break privacy completely, and I wrote that test and saw it fail when I removed the user_id filter.
- Why must each test start with a fresh database?
  - If old rows stay around from an earlier test, tests can interfere with each other and pass or fail depending on the order they run. Starting fresh keeps every test clean and repeatable.

## Mission 8: Package it, Docker (17 Nov 2026)

What I built:
- A Dockerfile: Python 3.14 slim image, requirements.txt copied and installed first, then the code, then uvicorn started on 0.0.0.0 port 8000
- A .dockerignore that keeps venv, caches, database files, .git, tests and .env out of the image
- A docker-compose.yml that builds the image, maps port 8000, sets SECRET_KEY and DATABASE_URL, and mounts ./data to /app/data so the database survives restarts
- Result: docker compose up --build started the app, /docs loaded, I registered, logged in and posted a 22:00 to 04:00 shift (6 hours, 87 pay)
- After stopping and starting again, the shift was still there, and data/shifts.db was on my Mac

What confused me:
- The whole idea at first. The meal-kit comparison helped: a Dockerfile is the recipe, an image is the finished kit and a container is one meal cooked from it
- docker info showed a client section but failed to connect to the server, because Docker Desktop was installed but not running
- A container called welcome-to-docker was already running. It is Docker Desktop's demo and uses port 8088, so it did not clash with my app
- In the compose file, spaces after the = signs would have become part of the values, and mounting a single file can make Docker create a folder in its place. I mounted the whole data folder instead

How I fixed it (and which hint level I needed):
- Opened Docker Desktop and waited until it was running, removed the spaces, and changed the volume to ./data:/app/data

Things I noticed:
- The build context was only about 35 kB, which shows .dockerignore kept my venv out
- The SECRET_KEY in the compose file is only a placeholder. The real key must be set on the host and never committed

One thing I would do differently:
- Check that the Docker engine is running (docker info) before writing any files

### Reflections
- What is the difference between an image and a container?
  - An image is the packaged template with the app code, dependencies, and runtime, like the meal kit. A container is an actual running instance of that image doing work.
- Why shouldn't the secret key be written in the Dockerfile?
  - Anything put in the Dockerfile ends up inside the image layers and can be inspected. The real secret key should be passed in as an environment variable at runtime, not baked into the image or repo.

## Mission 9: Ship it, README, CI, deploy and CV (18 Nov 2026)

What I built:
- A GitHub Actions workflow (.github/workflows/tests.yml) that installs requirements and runs pytest on every push. The first run passed with 7 tests on Python 3.14.10
- A README with a summary, features, tech used, how to run locally and with Docker, an endpoints table, a screenshot of /docs (docs/API.png) and what I learned
- A live deployment on Render using the Docker runtime and a long random SECRET_KEY set in Render's settings, with /docs loading at a public URL
- Pinned the repo on GitHub and added the project to LinkedIn and my CV

What confused me:
- The live site showed {"detail":"Not Found"} at the bare URL. That is normal, because the app has no page at "/" and the docs are at /docs
- GitHub showed a Node.js 20 deprecation warning and an ubuntu-latest migration notice on the first CI run. They did not stop it from passing
- A divergent branches error when I pushed. I had edited the README on GitHub (the live link) while also committing on my Mac, so Git would not guess how to join them
- .DS_Store files appeared as untracked files. I had to write the name with the capital S and no trailing slash to ignore them

How I fixed it (and which hint level I needed):
- Looked at the history with git log --graph, checked the GitHub commit with git show, then merged with git pull --no-rebase. The merge was clean and I did not force anything
- Added .DS_Store to .gitignore and committed the screenshot and README together

Things I noticed:
- On free hosting the app sleeps when idle and the SQLite database resets on every redeploy. That is fine for a demo, and I say so in the README

One thing I would do differently:
- Run git pull before starting work, and avoid editing files on GitHub while I am also committing locally

### Reflections
- Which decision in this project am I proudest of, and why?
  - Using get_own_shift and writing test_users_cannot_see_each_others_shifts so privacy wasn't just assumed. It was enforced in one place and proven by an automated test.
- What would I build next, and what would I do differently if I started again?
  - Next I'd move to PostgreSQL with proper migrations so data survives redeploys, and handle timezones properly. Starting over, I'd write automated tests and multi-user checks earlier instead of leaving them until later missions.


### reason for building this project:
- I used to work as a door supervisor, and working out my pay by hand was a pain, especially on night shifts like 10pm to 4am where the end time is earlier than the start. I was also studying Python and SQLite, so I decided to build something real for myself instead of doing exercises
I built a REST API with FastAPI. It tracks shifts, calculates hours and pay, handles overnight shifts, and gives a weekly summary. Users register and log in, passwords are hashed with argon2, and each user can only see their own data. I tested that with a second account and with an automated test. I also wrote tests that run on every push with GitHub Actions, packaged it with Docker, and deployed it online.
It’s a simple app, but it could be the back end of a bigger one with a proper front end. If I started again, I’d write the tests earlier. I only proved the privacy properly once I had two accounts.
