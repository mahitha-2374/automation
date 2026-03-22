# Testing Guide

## Unit Testing

### Test Schema Detection

```python
import unittest
from core.adaptive_engine import AdaptiveEngine
import pandas as pd

class TestAdaptiveEngine(unittest.TestCase):

    def setUp(self):
        self.engine = AdaptiveEngine()

    def test_user_detection(self):
        df = pd.DataFrame({'user_id': ['U001', 'U002']})
        mapping, _ = self.engine.detect_schema(df)
        self.assertEqual(mapping.get('user'), 'user_id')

    def test_role_detection(self):
        df = pd.DataFrame({'role_name': ['Admin', 'Viewer']})
        mapping, _ = self.engine.detect_schema(df)
        self.assertEqual(mapping.get('role'), 'role_name')
```

### Test Learning

```python
from core.learning_engine import LearningEngine

def test_learning_storage():
    mem = LearningEngine("test_memory.json")
    mem.store("TestCol", "user", 0.95)

    result = mem.get("TestCol")
    assert result["category"] == "user"
    assert result["confidence"] == 0.95
```

### Test Excel Generation

```python
from generators.excel_generator import ExcelGenerator

def test_excel_generation():
    data = {
        "users": [{"user_id": "U001", "roles": ["Admin"]}],
        "roles": [{"role_name": "Admin", "entitlements": ["Read"]}],
        "entitlements": [{"resource_name": "Read", "description": ""}]
    }

    gen = ExcelGenerator()
    gen.generate("templates/T3_template.xlsm", "test_output.xlsm", data)

    # Verify file exists and has data
    assert os.path.exists("test_output.xlsm")
```

## Integration Testing

### Full Pipeline Test

```python
def test_full_pipeline():
    # Create test data
    user_df = pd.DataFrame({
        'UserID': ['U001', 'U002'],
        'Role_Name': ['Admin', 'Viewer']
    })

    role_df = pd.DataFrame({
        'Role_Name': ['Admin', 'Viewer'],
        'ResName1': ['Create', 'Read']
    })

    # Process
    engine = AdaptiveEngine()
    result = engine.process(user_df, role_df)

    # Verify
    assert len(result['users']) == 2
    assert len(result['roles']) == 2
    assert len(result['entitlements']) >= 2
```

### API Testing

```python
import pytest
from api.server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_process(client):
    # Create test files
    data = {'user_file': (open('users.csv', 'rb'), 'users.csv'),
            'role_file': (open('roles.csv', 'rb'), 'roles.csv')}

    response = client.post('/process', data=data)
    assert response.status_code == 200
```

## Performance Testing

### Benchmark

```python
import time
import pandas as pd
from core.adaptive_engine import AdaptiveEngine

# Test with different sizes
sizes = [100, 1000, 10000]

for size in sizes:
    user_df = pd.DataFrame({
        'UserID': [f'U{i}' for i in range(size)],
        'Role': ['Admin'] * (size//2) + ['Viewer'] * (size//2)
    })

    engine = AdaptiveEngine()
    start = time.time()
    result = engine.process(user_df, user_df)
    elapsed = time.time() - start

    print(f"Size {size}: {elapsed:.2f}s")
```

Expected:

- 100 rows: < 1s
- 1000 rows: 1-3s
- 10000 rows: 5-10s

## UI Testing (Manual)

### Checklist

- [ ] File upload works
- [ ] Preview displays correctly
- [ ] Run button processes
- [ ] Summary tab shows metrics
- [ ] Users tab shows data
- [ ] Roles tab shows data
- [ ] Entitlements tab shows data
- [ ] Explainability shows mappings
- [ ] Excel download works
- [ ] Word download works
- [ ] Report download works
- [ ] Low confidence highlighted
- [ ] Confidence slider filters

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/

      - name: Lint
        run: pylint core/ generators/
```

## Load Testing

### Stress Test

```python
from concurrent.futures import ThreadPoolExecutor

def process_task():
    engine = AdaptiveEngine()
    user_df = pd.read_csv('test_users.csv')
    role_df = pd.read_csv('test_roles.csv')
    return engine.process(user_df, role_df)

# Test with 10 concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_task) for _ in range(10)]
    results = [f.result() for f in futures]

print(f"Processed {len(results)} requests successfully")
```

## Test Coverage

Target: 80%+ coverage

```bash
pip install coverage
coverage run -m pytest tests/
coverage report
coverage html
```

View `htmlcov/index.html` for detailed report.

## Troubleshooting Tests

### Model Download Issues

```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Memory Issues

```bash
# Run with memory limit
pytest --memray tests/test_large_files.py
```

### Flaky Tests

```python
import time

# Add retry logic
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_api_endpoint():
    """Retries up to 3 times with 1 second delay"""
    pass
```
