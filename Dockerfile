FROM python:3.5

# Make app dir
RUN mkdir /app


# Copy requirements.txt
COPY requirements.txt /app/requirements.txt
COPY requirements_test.txt /app/requirements_test.txt

WORKDIR /app

# Install dependencies with pip
RUN pip install -U pip && pip install -r /app/requirements.txt && pip install -r /app/requirements_test.txt
