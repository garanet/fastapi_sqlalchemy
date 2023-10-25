# pull the official docker image
FROM python:3.11.1-slim

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY ./app .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

# Expose the endpoint
EXPOSE 9000

# Run the endpoint
CMD ["python", "-u", "main.py"]