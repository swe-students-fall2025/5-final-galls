
FROM python:3.10

WORKDIR /app

# Copy dependency files
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pip install pipenv && pipenv install --system

# Copy project files
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
    