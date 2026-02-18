# CxC Fullstack (Flask backend + Next frontend)

This repository contains a Python Flask backend (with AI matching and a JSON API) and a Next.js frontend (Tailwind UI). The frontend proxies API requests to the Flask backend in development.

Run both servers (dev)

1. Install backend Python deps (if any):

   python3 -m pip install -r requirements.txt  # if you have a requirements.txt

2. Install frontend deps:

   cd frontend
   npm install

3. From the repo root start both servers with one command:

   npm run dev

This runs:
- Flask backend (python3 app.py) on http://localhost:5000
- Next frontend (npm run dev) on http://localhost:3000

Which URL to use in dev

- Open http://localhost:3000 — that's the Next frontend. It proxies /api/* to the Flask backend so you get the full AI/DB-powered experience.
- http://localhost:5000 is the backend; you can visit it directly to inspect the JSON endpoint at /api/listings.

Notes
- The Next dev server rewrites /api/* to the Flask backend (default http://localhost:5000). This avoids CORS and makes the frontend feel like a single app.
- If you prefer, you can run the backend and frontend separately using `npm run backend` and `npm run frontend`.
