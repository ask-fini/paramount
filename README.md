## paramount

Business Evals for LLMs

### Getting Started

#### Install Packages

**Server**

To enter Python Virtual Env

```py
source venv/bin/activate # and for exiting, deactivate
```

```py
pip install paramount # or python3 -m pip install paramount
```

**Client**

```py
cd client
pnpm i
```

#### Running

**Server**

This will run the server and the server will serve the client as well at `localhost:9001`

```py
gunicorn --bind :9001 --workers 1 --threads 8 --timeout 0 paramount.server.wsgi:app # or make run-server
```

Health Check: `localhost:9001/health`

**Client**

```py
cd client
pnpm dev  # or make run-client
```

#### Building the client

```shell
cd client
pnpm run build
```

### Environment Variables

There are two ways of accessing environment variables depending on the case of whether you'll use the client side with letting the server serve the static files or running both separately.

#### Using `.env` file

You need to also create some of the environment files with using `VITE_` prefix for the client. You can access the variables on client using `import.meta.env.<envVarName>`

```.env
FUNCTION_API_BASE_URL="http://localhost:9000"
PARAMOUNT_DB_TYPE="postgres"
PARAMOUNT_POSTGRES_CONNECTION_STRING=
PARAMOUNT_IDENTIFIER_COLNAME="input_args__company_uuid"
PARAMOUNT_META_COLS="['recorded_at']"
PARAMOUNT_INPUT_COLS="['args__message_history', 'args__new_question']"
PARAMOUNT_OUTPUT_COLS="['1_answer', '1_based_on']"
PARAMOUNT_IS_LIVE="TRUE"
PARAMOUNT_API_ENDPOINT="http://localhost:9001"
APP_ENV=development

VITE_META_COLS="["recorded_at"]"
VITE_INPUT_COLS="["args__message_history", "args__new_question"]"
VITE_OUTPUT_COLS="["1_answer", "1_based_on"]"
```

#### Using `.toml` file

You can access the variables on client like this;

```ts
import paramountConfig from "./paramount.toml";

console.log(paramountConfig);
```

Here is the [example toml file](https://github.com/ask-fini/paramount/blob/main/paramount/paramount.toml.example)

### Docker

By using just `Dockerfile.server`, you can containerize and deploy the whole package (including the client).

For running/deploying the server & client separately;

**Client**

```shell
docker build -t paramount-client -f Dockerfile.client . # or make docker-build-client
docker run -dp 3002:3002 paramount-client # or make docker-run-client
```

**Server**

```shell
docker build -t paramount-server -f Dockerfile.server . # or make docker-build-server
docker run -dp 9001:9001 paramount-server # or make docker-run-server
```

### TODOs

- ~~Fix env variables for the client~~ (`.toml` fix)
- ~~Refactor Dockerfile for the client~~ (Also file names have been changed for both client & server)
- ~~Allow Flask to serve the static files of the client~~
- Check the `.env` file access from Docker, add a prod check for the absolute path


### pypi upload procedure

prerequisite

```pip install wheel twine```

env vars for auth

```
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your_pypi_api_token>
```

build

```python setup.py sdist bdist_wheel```

upload

```twine upload dist/*```

