# CV Analyzer with LLM

FastAPI application built with Python using Hexagonal Architecture (Ports and Adapters) for analyzing CVs.

## Requirements

- Docker and Docker Compose (v2+)

## Running with Docker

1. **Configure Environment Variables**

   Copy `.env.template` to `.env` and fill in your API keys (e.g. `GEMINI_API_KEY`):
   ```bash
   cp .env.template .env
   ```

2. **Start the Application**

   - **Standard Mode**:
     ```bash
     docker compose up -d
     ```
   - **Development Mode (with Live Reload)**:
     ```bash
     docker compose -f docker-compose.yml -f docker-compose.dev.yml up
     ```

3. **Run Tests inside Container**

   Execute the pytest suite inside the isolated container without needing any host Python setup:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm cv-analyzer pytest
   ```

4. **Stop the Application**

   ```bash
   docker compose down
   ```

### Standalone Docker

- **Build image**:
  ```bash
  docker build -t cv-analyzer:latest .
  ```

- **Run container**:
  ```bash
  docker run -d --name cv_analyzer_api -p 8000:8000 --env-file .env cv-analyzer:latest
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

### CV Analysis (Cloud Fallback)

- **POST `/cv/analyze`**
  - **Summary**: Analyzes a candidate CV in PDF format against a job description using cloud LLMs with automated fallback.
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
      "match_percentage": 88,
      "provider": "gemini",
      "model": "gemini-3.8-flash"
    }
    ```

### CV Analysis (Local LLM - Ollama)

- **POST `/cv/analyze/local`**
  - **Summary**: Analyzes a candidate CV in PDF format against a job description using the local Ollama LLM (`qwen2.5:3b`) without external token costs or rate limits.
  - **Memory Persistence**: The model is loaded into memory on the first request and kept resident in memory indefinitely (`keep_alive=-1`) for fast subsequent evaluations.
  - **Content-Type**: `multipart/form-data`
  - **Parameters**: Same as `/cv/analyze` (`job_description`, `cv_file`).
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
      "match_percentage": 88,
      "provider": "ollama",
      "model": "qwen2.5:3b"
    }
    ```

## API Documentation

Once the application is running, access the API documentation at:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (also accessible at root `http://127.0.0.1:8000/`)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)