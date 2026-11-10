# frontend/src/lib/

Non-UI frontend code: the backend API client, formatting helpers and constants.

The backend base URL comes from `NEXT_PUBLIC_API_BASE_URL` (see `.env.example` in the repo root). Never put secrets in `NEXT_PUBLIC_` variables because they are exposed to the browser.
