FROM python:3.11-slim

WORKDIR /app
COPY ./src/ /app/src

# Set the PYTHONPATH to include the /app/src directory
ENV PYTHONPATH=/app/src

COPY ./pyproject.toml /code/pyproject.toml
RUN pip install /code/.

# Copy entrypoint.sh to the container
COPY ./src/entrypoint.sh /app/entrypoint.sh

# Make entrypoint.sh executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["sh", "/app/entrypoint.sh"]
