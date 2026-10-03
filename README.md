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

### CV Analysis

- **POST `/cv/analyze`**
  - **Summary**: Analyzes a candidate CV in PDF format against a job description.
  - **Content-Type**: `multipart/form-data`
  - **Parameters**:
    - `job_description` (Form text): Detailed job requirements and responsibilities.
    - `cv_file` (PDF file): Candidate CV document (processed in-memory, not stored on disk).
  - **Response (200 OK)**:
    ```json
    {
      "candidate_name": "Jane Doe",
      "years_of_experience": 5.0,
      "key_skills": ["Python", "FastAPI", "Docker", "LangChain"],
      "education": "B.S. in Computer Science - Tech University",
      "relevant_experience": "5 years designing scalable backend APIs...",
      "strengths": ["Deep FastAPI expertise", "Clean hexagonal architecture design"],
      "areas_for_improvement": ["Needs validation on Kubernetes cluster management"],
      "match_percentage": 88
    }
    ```

## API Documentation

Once the application is running, access the API documentation at:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (also accessible at root `http://127.0.0.1:8000/`)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)