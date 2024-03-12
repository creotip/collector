# LinkedIn collector

A service to collect data from LinkedIn

# Links

- Miro board that contains a diagram of the user profile and extracted data:
    - https://miro.com/app/board/uXjVNo980eU=/?share_link_id=555144013697

## Project tech stack

- 🌐 **Playwright**
- 🥁 **FastAPI**
- 🐍 **Pydantic**

## Installation

Install deps with poetry (it will install the relevant playwright browser)

```bash
make init
playwright install
```

## Requirements

Before running LinkedIn collector, you need to set LinkedIn credentials in `.env` file 

```bash
LINKEDIN_USERNAME=your_username
LINKEDIN_PASSWORD=your_password
```

Then run `test_login_and_save_cookies()`
This will save cookies in `./state/cookies.json` file.

From now on, you can access LinkedIn without logging in.

## Running the tests

run the tests with your IDE or with the following command:

```bash
poetry run pytest
```

> Note: You need to have cookies saved in `./state/cookies.json` file to run the tests.

## Running FastAPI server

```bash
make run
```

output:

```bash
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [96035] using StatReload
INFO:     Started server process [96041]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Search api endpoints

`/search/users` endpoint:

```http
http://127.0.0.1:8000/search/users?search_query=daniel%20goldberg
```

`/search/companies` endpoint:

```http
http://127.0.0.1:8000/search/companies?search_query=microsoft
```

> Note: Be patient, the search can be slow, as it's using Playwright to collect the data

### Exposing the local server to the internet

```bash
npx untun@latest tunnel http://127.0.0.1:8000
```

output:

```bash
◐ Starting cloudflared tunnel to http://127.0.0.1:8000                                                                                                                                                                                                                                                                                             5:12:40 PM
ℹ Waiting for tunnel URL...                                                                                                                                                                                                                                                                                                                       5:12:40 PM
✔ Tunnel ready at https://panama-research-elvis-glasgow.trycloudflare.com
```

> Note: Node.js is required to run the command above

## Saved data

Saved data from tests is stored in the [generated folder](tests/data/generated)


## How the data is extracted

The data is extracted using Playwright, a browser automation library.
**Here are the available methods and their documentation:**

- `login_to_linkedin()` - Logs in to LinkedIn in android mobile mode and saves cookies to `./state/cookies.json` file

- `search_users_flow()` - Searches for users in android mobile mode and returns a list of (n) user profile links with
  metadata.
- `search_companies_flow()` - Searches for companies in android tablet mode and returns a list of (n) company profile
  links
  with metadata (using android mobile mode)


**A diagram of the user profile and extracted data**
![collector - Frame 1](https://github.com/revrod/linkedin-collector/assets/3135968/b232984b-beb6-4a1a-bcbd-2822160d9e28)