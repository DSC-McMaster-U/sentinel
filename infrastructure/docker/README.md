# infrastructure/docker/

The backend development Dockerfile lives here to keep container configuration
with the rest of the infrastructure. Build from the repository root so Docker
can read the backend source and dependency file.

```sh
docker build -f infrastructure/docker/Dockerfile -t sentinel-backend-dev .
docker run --rm -p 127.0.0.1:8000:8000 sentinel-backend-dev
```

With the container running, open <http://127.0.0.1:8000/health> and expect
`{"status":"ok"}`. Press Ctrl+C to stop the server.

The server uses port 8000 by default. To verify a custom `PORT`, run:

```sh
docker run --rm -e PORT=8080 -p 127.0.0.1:8080:8080 sentinel-backend-dev
```

Then open <http://127.0.0.1:8080/health>.

To run the backend tests inside the same image:

```sh
docker run --rm sentinel-backend-dev python -m pytest
```

The FastAPI backend runs on its own. The MCP server is launched separately
over standard input/output by its client, so this setup uses a single container.
