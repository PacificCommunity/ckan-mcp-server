# CKAN MCP API Cookbook

**Copy-paste ready recipes for common data operations.**

> Get working code snippets and patterns for every task.

---

## 🍳 Table of Recipes

1. **Searching & Filtering** — Find datasets
2. **Pagination** — Handle large result sets
3. **Downloading Data** — Get files locally
4. **Accessing Data** — Query table records
5. **Organization Queries** — Org-specific data
6. **Error Handling** — Deal with issues gracefully
7. **Data Processing** — Transform results
8. **Automation** — Batch operations

---

## 🔍 Searching & Filtering

### Recipe 1: Basic Search
**Task**: Find datasets matching keywords

**Ask Claude:**
```
"Search for datasets about 'climate'"
```

**What Claude Runs**:
```python
# Under the hood
ckan_package_search(q="climate", rows=10)
```

**Result**: First 10 climate-related datasets

---

### Recipe 2: Filter by Organization
**Task**: Get datasets from specific department

**Ask Claude:**
```
"Find all datasets from the Health Department"
```

**What Claude Runs**:
```python
# Filter by organization
ckan_package_search(
    fq="organization:health-department",
    rows=50
)
```

**Tips**:
- Organization name must match exactly (case-insensitive)
- Use IDs or slugs from `ckan_organization_list()` if unsure

---

### Recipe 3: Filter by File Format
**Task**: Get only CSV files

**Ask Claude:**
```
"Find all CSV files in our portal"
```

**What Claude Runs**:
```python
ckan_package_search(
    q="*:*",  # All datasets
    fq="res_format:CSV",  # Only CSV resources
    rows=100
)
```

**Supported Formats**:
- CSV, JSON, XML, Excel, PDF
- Shapefile, GeoJSON, NetCDF
- API, SPARQL, and more

---

### Recipe 4: Combine Multiple Filters
**Task**: CSV files from Health Dept, updated recently

**Ask Claude:**
```
"Find CSV files from Health Department updated in the last 30 days"
```

**What Claude Runs**:
```python
ckan_package_search(
    fq="organization:health AND res_format:CSV",
    sort="metadata_modified desc",
    rows=50
)
```

**Pattern**:
```
fq="field1:value1 AND field2:value2"
```

---

### Recipe 5: Search by Tag
**Task**: Find all datasets tagged "open-data"

**Ask Claude:**
```
"Show all datasets with the 'open-data' tag"
```

**What Claude Runs**:
```python
ckan_package_search(
    fq="tags:open-data",
    rows=100
)
```

---

### Recipe 6: Exclude Results
**Task**: Find datasets but exclude private ones

**Ask Claude:**
```
"Search for health datasets (public only)"
```

**What Claude Runs**:
```python
ckan_package_search(
    q="health",
    include_private=False,
    rows=50
)
```

---

## 📄 Pagination

### Recipe 7: Get All Results (Paginated)
**Task**: Download all 500 datasets

**Ask Claude:**
```
"Export a list of all datasets in the portal"
```

**What Claude Does**:
```python
all_datasets = []

# Page 1
page1 = ckan_package_search(
    q="*:*",
    rows=100,
    start=0
)
all_datasets.extend(page1['results'])

# Page 2
page2 = ckan_package_search(
    q="*:*",
    rows=100,
    start=100
)
all_datasets.extend(page2['results'])

# Continue until no more results...
# Total: all_datasets contains all datasets
```

**Pattern**:
- Use `rows` for batch size (100 is good)
- Use `start` to skip ahead
- Loop until results < batch size

---

### Recipe 8: Offset-Based Pagination
**Task**: Browse through results 10 at a time

**Ask Claude:**
```
"Show me page 1 of datasets (10 per page)"
"Show page 2"
"Show page 3"
```

**Pattern**:
```
Page 1: start=0,   rows=10
Page 2: start=10,  rows=10
Page 3: start=20,  rows=10
Page N: start=(N-1)*10, rows=10
```

---

## 💾 Downloading Data

### Recipe 9: Download Single File
**Task**: Save a dataset file locally

**Ask Claude:**
```
"Download the 'Annual Budget 2024' dataset to my computer"
```

**What Claude Runs**:
```python
# Find the dataset
dataset = ckan_package_show(id="annual-budget-2024")

# Get first resource
resource_id = dataset['resources'][0]['id']

# Download
ckan_resource_download(
    resource_id=resource_id,
    output_folder="/home/user/downloads",
    output_format="file"
)
```

**Result**: File saved to ~/downloads/annual-budget-2024.csv

---

### Recipe 10: Download All Resources from Dataset
**Task**: Get all files from one dataset

**Ask Claude:**
```
"Download all resources from the Climate Data dataset"
```

**What Claude Does**:
```python
# Get dataset
dataset = ckan_package_show(id="climate-data")

# Download each resource
for resource in dataset['resources']:
    ckan_resource_download(
        resource_id=resource['id'],
        output_folder="/home/user/downloads",
        output_format="file"
    )

# Result: All files saved locally
```

---

### Recipe 11: Download and Parse JSON
**Task**: Get data as JSON for processing

**Ask Claude:**
```
"Download the budget data as JSON and analyze it"
```

**What Claude Runs**:
```python
result = ckan_resource_download(
    resource_id="resource-id",
    output_folder="/home/user/downloads",
    output_format="json"  # ← Parse as JSON
)

# result now contains parsed JSON data
data = result['data']  # Access the records
```

---

## 🔍 Accessing Data (Queries)

### Recipe 12: Query Tabular Data
**Task**: Get records from a DataStore table

**Ask Claude:**
```
"Show me the first 100 rows of budget data"
```

**What Claude Runs**:
```python
ckan_datastore_search(
    resource_id="resource-uuid",
    limit=100,
    offset=0
)
```

---

### Recipe 13: Filter Query Results
**Task**: Find records matching criteria

**Ask Claude:**
```
"Show budget records where amount > $100,000"
```

**What Claude Runs**:
```python
ckan_datastore_search(
    resource_id="budget-table",
    q="amount:>100000",  # Full-text search
    limit=50
)
```

---

### Recipe 14: Sort Query Results
**Task**: Get most recent records first

**Ask Claude:**
```
"Show the latest 20 transactions, most recent first"
```

**What Claude Runs**:
```python
ckan_datastore_search(
    resource_id="transactions-table",
    sort="date desc",  # desc = descending
    limit=20
)
```

**Sort Examples**:
```
sort="date desc"           # Newest first
sort="date asc"            # Oldest first
sort="amount desc"         # Highest first
sort="name asc"            # A-Z order
sort="created_date desc"   # Recent updates first
```

---

### Recipe 15: Get Specific Columns Only
**Task**: Reduce data size by selecting columns

**Ask Claude:**
```
"Show me just date and amount from budget records"
```

**What Claude Runs**:
```python
ckan_datastore_search(
    resource_id="budget-table",
    fields=["date", "amount"],  # Only these columns
    limit=100
)
```

---

### Recipe 16: Paginate Through Large Dataset
**Task**: Process 10,000 records in batches

**Ask Claude:**
```
"Export all budget records (showing progress)"
```

**Pattern**:
```python
all_records = []
batch_size = 100

offset = 0
while True:
    batch = ckan_datastore_search(
        resource_id="id",
        limit=batch_size,
        offset=offset
    )
    
    if not batch['records']:
        break  # No more data
    
    all_records.extend(batch['records'])
    offset += batch_size

# all_records now has all data
```

---

## 🏢 Organization Queries

### Recipe 17: Get All Org Datasets
**Task**: List everything published by a department

**Ask Claude:**
```
"Show all datasets from the Transportation Department"
```

**What Claude Runs**:
```python
ckan_organization_show(
    id="transportation",
    include_datasets=True  # ← Include all datasets
)
```

**Result**: Org info + all published datasets

---

### Recipe 18: Org Details
**Task**: Get organization metadata

**Ask Claude:**
```
"Get contact information for the Finance Department"
```

**What Claude Runs**:
```python
ckan_organization_show(
    id="finance",
    include_datasets=False  # Just org info
)
```

**Info Returned**:
- Name, title, description
- Contact email/URL
- Logo/image
- Member count
- Creation/update dates

---

### Recipe 19: List All Organizations
**Task**: See all departments

**Ask Claude:**
```
"List all organizations in the portal"
```

**What Claude Runs**:
```python
ckan_organization_list(all_fields=True)
```

---

## ⚠️ Error Handling

### Recipe 20: Handle Missing Dataset
**Task**: Gracefully respond if dataset not found

**Ask Claude:**
```
"Try to find dataset 'nonexistent-data'"
```

**Pattern**:
```python
try:
    dataset = ckan_package_show(id="nonexistent")
except:
    print("Dataset not found. Try searching instead.")
    # Fall back to search
    results = ckan_package_search(q="search-term")
```

---

### Recipe 21: Handle Large Results
**Task**: Don't overwhelm user with 10,000 results

**Pattern**:
```python
results = ckan_package_search(q="*:*", rows=1000)

if len(results) >= 1000:
    print("Too many results (1000+)")
    print("Try narrowing search with filters")
else:
    print(f"Found {len(results)} datasets")
```

---

### Recipe 22: Validate API Key
**Task**: Test if credentials work

**Ask Claude:**
```
"Test the connection to the CKAN portal"
```

**What Claude Runs**:
```python
try:
    status = ckan_status_show()
    print("✅ Connection OK")
except:
    print("❌ Cannot reach CKAN")
    print("Check CKAN_URL and API_KEY")
```

---

## 🔄 Data Processing

### Recipe 23: Parse Search Results
**Task**: Extract useful info from search

**Pattern**:
```python
results = ckan_package_search(q="climate")

for dataset in results['results']:
    title = dataset.get('title', 'Untitled')
    org = dataset.get('organization', {}).get('name', 'Unknown')
    updated = dataset.get('metadata_modified', 'N/A')
    
    print(f"{title} ({org}) - Updated: {updated}")
```

---

### Recipe 24: Collect Metadata
**Task**: Build spreadsheet of dataset info

**Pattern**:
```python
datasets = ckan_package_list()
inventory = []

for dataset_id in datasets:
    dataset = ckan_package_show(id=dataset_id)
    
    inventory.append({
        'id': dataset['id'],
        'title': dataset['title'],
        'org': dataset['organization']['name'],
        'created': dataset['metadata_created'],
        'resources': len(dataset['resources']),
        'formats': ', '.join([
            r['format'] for r in dataset['resources']
        ])
    })

# inventory can now be exported to CSV
```

---

## 🤖 Automation

### Recipe 25: Monitor Datasets
**Task**: Alert if dataset not updated recently

**Pattern**:
```python
from datetime import datetime, timedelta

datasets = ckan_package_search(q="*:*", rows=1000)
stale_days = 180

for dataset in datasets['results']:
    last_update = datetime.fromisoformat(
        dataset['metadata_modified']
    )
    days_old = (datetime.now() - last_update).days
    
    if days_old > stale_days:
        print(f"⚠️  {dataset['title']} - {days_old} days old")
```

---

### Recipe 26: Batch Download by Organization
**Task**: Download all org's CSV files

**Pattern**:
```python
# Get org and all its datasets
org = ckan_organization_show(
    id="finance",
    include_datasets=True
)

# For each dataset, find CSVs and download
for dataset in org['packages']:
    for resource in dataset['resources']:
        if resource['format'].upper() == 'CSV':
            ckan_resource_download(
                resource_id=resource['id'],
                output_folder="/downloads/finance",
                output_format="file"
            )
```

---

### Recipe 27: Check Data Quality
**Task**: Find datasets with missing descriptions

**Pattern**:
```python
datasets = ckan_package_list()
quality_issues = []

for dataset_id in datasets:
    dataset = ckan_package_show(id=dataset_id)
    
    # Check for quality issues
    if not dataset.get('notes'):
        quality_issues.append({
            'dataset': dataset_id,
            'issue': 'Missing description'
        })
    
    if not dataset.get('resources'):
        quality_issues.append({
            'dataset': dataset_id,
            'issue': 'No resources'
        })

print(f"Found {len(quality_issues)} quality issues")
```

---

## 📊 Common Query Parameters

### Search Parameters
```python
ckan_package_search(
    q="climate",           # Search term
    fq="organization:x",   # Filter
    sort="score desc",     # Sort field + direction
    rows=50,              # Results per request
    start=0               # Pagination offset
)
```

### DataStore Parameters
```python
ckan_datastore_search(
    resource_id="uuid",   # Required: resource ID
    q="query",            # Optional: search
    sort="col desc",      # Optional: sort
    limit=100,            # Optional: page size
    offset=0,             # Optional: offset
    fields=["col1"]       # Optional: columns
)
```

### Download Parameters
```python
ckan_resource_download(
    resource_id="uuid",              # Required
    output_folder="/path",           # Required
    output_format="file"             # "file"|"json"|"raw"
)
```

---

## 🎯 Quick Reference Table

| Task | Tool | Key Parameter |
|------|------|----------------|
| Search | `ckan_package_search` | `q="keywords"` |
| Filter | `ckan_package_search` | `fq="field:value"` |
| Get all | `ckan_package_list` | `limit=100` |
| Details | `ckan_package_show` | `id="id"` |
| Query data | `ckan_datastore_search` | `resource_id="id"` |
| Download | `ckan_resource_download` | `resource_id="id"` |
| Org info | `ckan_organization_show` | `id="name"` |

---

## 💡 Pro Tips

### ✅ DO
- Start with specific searches (use `q` parameter)
- Use filters to narrow results before downloading
- Paginate when you need many results
- Handle errors gracefully
- Cache results when possible

### ❌ DON'T
- Request all results at once (can be slow/memory intensive)
- Download files you don't need
- Make repeated calls for same data
- Use complex queries without filters
- Ignore API rate limits

---

## 📚 Learn More

- **Setup**: [Quick Start Guide](./QUICK_START_ADMIN.md)
- **Real examples**: [Scenario Examples](./SCENARIO_EXAMPLES.md)
- **All tools**: [Tool Capabilities](./TOOL_CAPABILITIES.md)
- **By use case**: [Tools by Use Case](./TOOLS_BY_USE_CASE.md)

---

**Version**: CKAN MCP API Cookbook v1.0  
**Audience**: Data analysts, developers, automation specialists  
**Last Updated**: Phase 2 Implementation
