# CV Analyzer with LLM

FastAPI application built with Python using Hexagonal Architecture (Ports and Adapters) for analyzing CVs.

## Requirements

- Python 3.9+

## Step-by-Step Setup

1. **Create and Activate Virtual Environment**

   On Windows (PowerShell):
   ```powershell
   python -m venv ..\venv
   ..\venv\Scripts\activate
   ```

   On Linux / macOS:
   ```bash
   python3 -m venv ../venv
   source ../venv/bin/activate
   ```

2. **Install Dependencies**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the Application**

   ```powershell
   uvicorn cv_analyzer.main:app --reload --app-dir src
   ```

4. **Run Tests**

   ```powershell
   pytest
   ```

## Available Endpoints

### Health Check

- **GET `/health`**
  - **Summary**: Returns the health status of the application.
  - **Response (200 OK)**:
    ```json
    {
      "status": "ok"
    }
    ```

## API Documentation

Once the application is running, access the API documentation at:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (also accessible at root `http://127.0.0.1:8000/`)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)