## paramount

Business Evals for LLMs

## Getting Started

#### Install Packages

**Server**

```py
pip install paramount # or python3 -m pip install paramount
```

**Client**

```py
pnpm i
```

#### Running

**Server**

```py
gunicorn --bind :9001 --workers 1 --threads 8 --timeout 0 paramount.server.wsgi:app # or make run-server
```

**Client**

```py
cd client
pnpm dev  # or make run-client
```

### TODOs

- Fix env variables for the client
- Refactor Dockerfile for the client
