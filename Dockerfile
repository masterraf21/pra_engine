FROM python:3.10.4-slim-bullseye

# # create the app user
# RUN addgroup --system app && adduser --system --group app
WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.0.0

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock ./

# RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY src/ /app/src/
COPY run_engine.py log_config.yaml /app/

# RUN chmod +x run.sh

# ENV PYTHONPATH=/app

# # chown all the files to the app user
# RUN chown -R app:app $HOME

# # change to the app user
# # Switch to a non-root user, which is recommended by Heroku.
# USER app

# Run the run script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Uvicorn
CMD ["poetry","run","python","run_engine.py"]