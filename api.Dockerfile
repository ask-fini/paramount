# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Allow installation of deprecated sklearn package. This is required by scrubadub -> textblob -> sklearn
ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True

# Set the working directory for the application
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy all the necessary project files into the container
COPY . $APP_HOME/

RUN pip install --no-cache-dir .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 paramount.wsgi:app