# API Usage Examples

## 1. Basic Processing

### Python

```python
import requests

files = {
    'user_file': open('users.csv', 'rb'),
    'role_file': open('roles.csv', 'rb')
}

response = requests.post('http://localhost:5000/process', files=files)
data = response.json()
print(f"Users: {len(data['users'])}")
print(f"Roles: {len(data['roles'])}")
```

### cURL

```bash
curl -X POST http://localhost:5000/process \
  -F "user_file=@users.csv" \
  -F "role_file=@roles.csv"
```

## 2. Download Excel

### Python

```python
import requests

files = {
    'user_file': open('users.csv', 'rb'),
    'role_file': open('roles.csv', 'rb')
}

response = requests.post('http://localhost:5000/process/excel', files=files)

with open('T3_output.xlsm', 'wb') as f:
    f.write(response.content)
```

### cURL

```bash
curl -X POST http://localhost:5000/process/excel \
  -F "user_file=@users.csv" \
  -F "role_file=@roles.csv" \
  -o T3_output.xlsm
```

## 3. Download Word

```bash
curl -X POST http://localhost:5000/process/word \
  -F "user_file=@users.csv" \
  -F "role_file=@roles.csv" \
  -o OLA_output.docx
```

## 4. Schema Detection Only

```bash
curl -X POST http://localhost:5000/schema/detect \
  -F "file=@users.csv" | jq .
```

Response:

```json
{
  "mapping": {
    "user": "UserID",
    "role": "Role_Name"
  },
  "explanations": [
    {
      "column": "UserID",
      "mapped_as": "user",
      "confidence": 0.95,
      "source": "semantic"
    }
  ]
}
```

## 5. Health Check

```bash
curl http://localhost:5000/health
```

Response:

```json
{
  "status": "healthy",
  "service": "IAM Automation Platform",
  "version": "1.0"
}
```

## 6. Learning Memory

### View Memory

```bash
curl http://localhost:5000/learning/memory | jq .
```

### Clear Memory

```bash
curl -X DELETE http://localhost:5000/learning/memory
```

## Integration Examples

### Scheduled Task (Windows Task Scheduler)

1. Create `run_automation.bat`:

```batch
@echo off
cd C:\iam_automation
python main.py ^
  --user input\users_export.csv ^
  --role input\roles_export.csv ^
  --output-dir output
```

2. Schedule via `taskschd.msc`

### Scheduled Task (Linux Cron)

```bash
0 2 * * * cd /opt/iam_automation && python main.py \
  --user input/users_export.csv \
  --role input/roles_export.csv
```

### PowerShell Script

```powershell
$url = "http://localhost:5000/process/excel"
$userFile = "C:\exports\users.csv"
$roleFile = "C:\exports\roles.csv"

$form = @{
    user_file = Get-Item -Path $userFile
    role_file = Get-Item -Path $roleFile
}

$response = Invoke-WebRequest -Uri $url -Method Post -Form $form
[IO.File]::WriteAllBytes("C:\output\T3_output.xlsm", $response.Content)
```

## Error Handling

### File Not Found

Request:

```bash
curl -X POST http://localhost:5000/process \
  -F "user_file=@nonexistent.csv" \
  -F "role_file=@roles.csv"
```

Response:

```json
{
  "error": "Missing files"
}
```

### Invalid CSV

Response:

```json
{
  "error": "Error parsing CSV: UTF-8 codec error",
  "traceback": "..."
}
```

## Rate Limiting

No built-in rate limiting. For production, add:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/process', methods=['POST'])
@limiter.limit("10 per hour")
def process():
    ...
```

## Authentication

For secured deployments, add:

```python
from functools import wraps
from flask import request

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token or token != os.getenv('API_TOKEN'):
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated

@app.route('/process', methods=['POST'])
@token_required
def process():
    ...
```

Usage:

```bash
curl -H "X-API-Token: your-secret-token" \
  -X POST http://localhost:5000/process \
  -F "user_file=@users.csv" \
  -F "role_file=@roles.csv"
```
