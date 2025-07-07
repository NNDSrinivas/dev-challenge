### PowerShell Quickstart

```powershell
# 1) POST a new job
$body = @{ input_text = "Can you give me info about Virat Kohli in a short para" } | ConvertTo-Json
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8000/jobs/ -Headers @{ "Content-Type" = "application/json" } -Body $body

# 2) Inspect the full response
$response | Format-List *

# 3) Capture the event_id
$id = $response.event_id
if ([string]::IsNullOrEmpty($id)) {
  Write-Error "POST failed to return an event_id"
  return
}

# 4) GET the job status/result
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/jobs/$id/"
