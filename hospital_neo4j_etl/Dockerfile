FROM python:3.11-slim 

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY src/ /app

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["sh", "entrypoint.sh"]
