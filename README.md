# UniSync
A project that scrapes schedule data from SNU's ERP and integrates it into your google calendar.

# Steps to run locally
1. Clone this repository and navigate into it.
2. Create a `.env` file and enter your net id and password like shown:
```
NETID = "lm742"
PASSWORD = "ThisIsntMyPassword"
```
3. Create a directory `./secrets`
4. Go onto Google Cloud Console and create a Project (name it whatever you want).
5. Configure your OAuth Consent screen (for help, email me).
    - Add `./auth/calendar` under your scopes.
6. Goto credentials and make a OAuth Client ID.
    - Select `Web Application` and name it whatever
    - Under `Authorized rediredt URIs` add `http://localhost/`
    - Save the credential and save it as a json file.
7. Rename the json file you just saved to `client_secret.json` and save it in the `./secrets` directory in step 3.
8. Create a virtual environment like so `python -m venv ./__venv__`
9. Activate your virtual enviroment.
10. Run `pip install -r requirements.txt` (Step 8 and 9 can be skipped if you're fine with global installation).
- Your file structure should look something like this
```
---
 |-- __venv__
 |-- Secrets
 |      |-- client_secret.json
 |-- .env
 |-- .gitignore
 |-- main.py
 |-- README.md
 |-- requirements.txt
```
11. Run `main.py` \:D

# TODO
- Create loading bars when the script is being run.