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