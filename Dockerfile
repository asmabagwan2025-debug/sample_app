# Step 1: Use an official lightweight Python image
FROM python:3.9-slim

# Step 2: Set the working directory
WORKDIR /code

# Step 3: Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the application code into the container
COPY ./main.py /code/main.py

# Step 5: FastAPI default port is often 8000
EXPOSE 8000

# Step 6: Run the application using Uvicorn
# Syntax: uvicorn <filename>:<app_variable_name> --host 0.0.0.0 --port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]