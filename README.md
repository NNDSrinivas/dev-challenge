````markdown
# Dev Challenge: Async Job Processing API

I built a minimal backend service to demonstrate a clean, pragmatic approach
to handling asynchronous “jobs” with AI. You can POST arbitrary guideline text,
have a worker run a two-step GPT chain (summarize → checklist), then retrieve
the job’s status and results.


---

## Tech Stack

- **Python 3.11**  
- **Django 4.x** + **Django REST Framework**  
- **Celery** + **Redis** (broker & result backend)  
- **PostgreSQL**  
- **OpenAI Python v1 SDK**  
- **Docker** + **docker-compose**  
- **drf-spectacular** for auto-generated OpenAPI/Swagger

---

## Quickstart

1. **Clone & enter**  
   ```bash
   git clone https://github.com/<you>/dev-challenge.git
   cd dev-challenge
````

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env:
   #  - SECRET_KEY (Django)
   #  - OPENAI_API_KEY
   #  - DATABASE_URL, REDIS_URL
   ```

3. **Build & run**

   ```bash
   docker-compose up --build -d
   ```

4. **Verify**

   * Django:  [http://localhost:8000/](http://localhost:8000/)
   * Swagger: [http://localhost:8000/docs/](http://localhost:8000/docs/)

---

## API Endpoints

### Enqueue a job

**POST** `/jobs/`
*Request*

```json
{ "input_text": "Review security guidelines: check firewall, audit logs, encryption." }
```

*Response (201)*

```json
{ "event_id": "7d217a36-6826-4758-8191-6e3ed57aa722" }
```

### Poll job status & results

**GET** `/jobs/{event_id}/`
*Response (200)*

```json
{
  "id": "7d217a36-6826-4758-8191-6e3ed57aa722",
  "input_text": "...",
  "status": "pending|running|succeeded|failed",
  "summary":   "...GPT-generated summary...",
  "checklist": "- Bullet 1\n- Bullet 2\n…",
  "created_at":"2025-07-06T23:19:47Z",
  "updated_at":"2025-07-06T23:19:52Z"
}
```

---

## CLI Examples

#### Linux/macOS (curl)

```bash
# Enqueue
curl -X POST http://localhost:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"input_text":"Tell me about Shubman Gill"}'

# Poll
curl http://localhost:8000/jobs/7d217a36-6826-4758-8191-6e3ed57aa722/
```

#### PowerShell

```powershell
# POST
$body = @{ input_text = "Tell me about Shubman Gill" } | ConvertTo-Json
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8000/jobs/ `
  -Headers @{ "Content-Type" = "application/json" } -Body $body
$id = $response.event_id

# GET (loop until succeeded)
do {
  $job = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/jobs/$id/"
  Write-Host "Status:" $job.status
  if ($job.status -in @("pending","running")) { Start-Sleep 2 }
} while ($job.status -in @("pending","running"))
$job | ConvertTo-Json
```

---

## Interactive Docs

Play with the endpoints in your browser:
[http://localhost:8000/docs/](http://localhost:8000/docs/)

---

## Testing & Coverage

I’ve written unit tests for models, serializers, views, and the Celery task. To run tests:

```bash
docker-compose run --rm web python manage.py test
```

To measure and report coverage:

1. **Install** `coverage` in `requirements.txt`
2. **Configure** `.coveragerc` to focus on `api/` and `jobs/` and omit tests/admin stubs.
3. **Collect data**:

   ```bash
   docker-compose run --rm web coverage run manage.py test
   ```
4. **View report**:

   ```bash
   docker-compose run --rm web coverage report -m
   ```

Aim: ≥70% coverage across all application code.

---

## Admin UI (optional)

To inspect jobs via Django admin:

```bash
docker-compose run --rm web python manage.py createsuperuser
```

Visit [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## License

This project is licensed under the **MIT License**—see [LICENSE](LICENSE).

---


# dev-challenge