# Architecture & Design

## System Overview

```
┌─────────────────────────────────────────────┐
│           User Input (CSV Files)            │
└────────────────────┬────────────────────────┘
                    │
┌────────────────────▼────────────────────────┐
│       Adaptive Schema Detection            │
│  ┌─────────────────────────────────────┐   │
│  │ 1. Check Learning Memory            │   │
│  │ 2. Semantic Matching (if not found) │   │
│  │ 3. Store for Future Learning        │   │
│  └─────────────────────────────────────┘   │
└────────────────────┬────────────────────────┘
                    │
┌────────────────────▼────────────────────────┐
│     Data Processing & Mapping               │
│  ┌─────────────────────────────────────┐   │
│  │ • User → Role Mapping               │   │
│  │ • Role → Entitlement Mapping        │   │
│  │ • Hierarchy Building                │   │
│  │ • Description Generation            │   │
│  └─────────────────────────────────────┘   │
└────────────────────┬────────────────────────┘
                    │
┌────────────────────▼────────────────────────┐
│    Validation & Explainability              │
│  ┌─────────────────────────────────────┐   │
│  │ • Missing role detection            │   │
│  │ • Confidence scoring                │   │
│  │ • Audit trail generation            │   │
│  └─────────────────────────────────────┘   │
└────────────────────┬────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
   ┌────▼────┐ ┌────▼────┐ ┌───▼─────┐
   │  Excel  │ │  Word   │ │ Report  │
   │ Output  │ │ Output  │ │ Output  │
   └─────────┘ └─────────┘ └─────────┘
```

## Component Architecture

### 1. Semantic Engine

**Purpose:** Understand column meaning

**Implementation:**

- Uses sentence-transformers (all-MiniLM-L6-v2)
- Creates embeddings for both columns and IAM concepts
- Matches via cosine similarity

**Key Features:**

- Works offline (downloads model once)
- Handles partial matches
- Confidence scoring

```
Input: "AccessBundle" → Embedding → Cosine Similarity → "role" (0.82)
```

### 2. Learning Engine

**Purpose:** Store and reuse successful mappings

**Storage:** JSON file (`memory/knowledge.json`)

**Lifecycle:**

1. First run: Semantic detection
2. Store in memory
3. Second run: Direct retrieval (0.001s vs 0.5s)4. User correction: Update memory

**Format:**

```json
{
  "mappings": {
    "userid": {
      "category": "user",
      "confidence": 0.95,
      "learned_at": "2024-01-15T10:30:00"
    }
  },
  "history": [...]
}
```

### 3. Adaptive Engine

**Purpose:** Orchestrate entire pipeline

**Flow:**

1. Load data
2. Detect schemas
3. Build mappings
4. Generate descriptions
5. Return structured data

**Key Logic:**

```python
# Automatic entitlement building
["module", "category", "subcategory", "permission"]
↓
For each, find in row
↓
Join with " > "
↓
"Admin > System > Security > Modify"
```

### 4. Explainer

**Purpose:** Generate audit trails

**Output:**

```json
{
  "column": "UserID",
  "mapped_as": "user",
  "confidence": 0.95,
  "source": "semantic",
  "reason": "UserID was interpreted as user using semantic matching"
}
```

## Data Flow

### Input Processing

```
CSV Input
  ↓
  Load with Pandas
  ↓
  Normalize column names
  ↓
  Handle null/empty values
  ↓
  Schema detection
  ↓
  Ready for processing
```

### User-Role Mapping

```
For each row:
  Extract user ID
  Extract role name

  If not in user_map:
    Create entry

  Add role to list (no duplicates)
```

### Role-Entitlement Mapping

```
For each role row:
  Extract role name
  Build entitlement dynamically

  If role not seen:
    Create role entry

  Add entitlement to list
  Create entitlement object
```

### Hierarchy Building

**Dynamic:**

- If module exists → use
- If category exists → use
- If subcategory exists → use
- If permission exists → use only if nothing above

**Example:**

- Row has: module="Admin", category="Security", subcategory="Admin"
- Entitlement: "Admin > Security > Admin"

## Learning Mechanism

### Training Process

```
Run 1:
  Column "user_identifier"
  → Semantic: matches "user" (0.88)
  → Store: user_identifier ↔ user

Run 2:
  Column "user_identifier"
  → Memory: found! user ↔ 0.88
  → Use directly (10x faster)

Run 3:
  User corrects: actually "role" not "user"
  → Update memory
  → Future runs: correct forever
```

### Confidence Scoring

```
Semantic score alone: 0.88
Multiple matches: average
Rule-based boost: +0.05 if name contains "user"
Final: 0.93
```

## Output Generation

### Excel (T3)

Sheets filled:

1. **User_role_resource** - Raw data (users get roles)
2. **Role_Resource** - Roles get entitlements
3. **Role_resource_lookup** - Reference (roles + entitlements)
4. **User_Account_lookup** - User details
5. **gsi_user-role-resource-cntrl** - Control (counts + date)

**Safety Features:**

- Opens in keep_vba mode
- Only overwrites data cells
- Preserves all formulas
- Never touches formula sheets

### Word (OLA)

Template placeholders:

```
<<SYSTEM_ID>> → SYS_001
<<USER_COUNT>> → 47
{{ROLE_COUNT}} → 12
```

**Safety Features:**

- Only replaces defined placeholders
- Never touches unrelated content
- Preserves formatting

### Report (Audit)

Two sheets:

1. **Mappings** - Every column, confidence, source
2. **Summary** - Statistics (high/med/low confidence)

## Error Handling

### Missing Data

```python
if pd.notna(value):
    # safe to use
else:
    # skip or default
```

### Encoding Issues

```python
try:
    df = pd.read_csv(file)
except:
    df = pd.read_csv(file, encoding='latin-1')
```

### Duplicate Handling

- User → Role: No duplicates (set)
- Role → Entitlement: No duplicates (set)

## Performance Optimization

### Semantic Matching

- Pre-encode concept vectors (one-time)
- Batch process columns
- Cache results

### Data Processing

- Vectorized operations (Pandas)
- Minimal loops
- Early termination

### Memory

- Stream large files
- Delete intermediate objects
- Lazy loading

## Security Considerations

### Input Validation

✅ CSV file format checked
✅ Size limits imposed (16MB)
✅ No code execution

### Output Handling

✅ Data only (no templates rewritten)
✅ File paths sanitized
✅ No path traversal

### API

❌ No authentication (add in production)
❌ No rate limiting (add in production)
✅ Error messages safe (not exposing internals)

### Learning Memory

✅ JSON only (no code)
✅ Persisted locally (no cloud)
✅ Can be cleared anytime

## Scalability

### Current Limits

- File size: < 1GB
- Rows: < 1M
- Columns: < 100
- Processing: < 60 seconds

### Scaling Options

1. **Streaming** - Process chunks
2. **Batch** - Queue jobs
3. **Distributed** - Multiple workers
4. **Database** - Replace CSV→SQL

## Testing Strategy

### Unit Tests

- Schema detection accuracy
- Mapping correctness
- Learning storage

### Integration Tests

- End-to-end pipeline
- Excel generation
- Word generation

### Performance Tests

- Large file handling
- Memory usage
- Speed benchmarks

## Deployment Models

| Model     | Use Case         | Complexity     |
| --------- | ---------------- | -------------- |
| Streamlit | Web UI           | ⭐ Simple      |
| Flask     | API integration  | ⭐⭐ Medium    |
| CLI       | Scheduled jobs   | ⭐ Simple      |
| Docker    | Cloud deployment | ⭐⭐⭐ Complex |

---

**Key Insight:** This architecture separates concerns perfectly—schema detection doesn't know about Excel generation, learning doesn't know about output, etc. Each component can be tested and upgraded independently.
