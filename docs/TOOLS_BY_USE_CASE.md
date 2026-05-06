# CKAN MCP Tools by Use Case

A practical guide to using CKAN MCP Server tools for common data management and exploration tasks.

---

## 🔍 Data Discovery & Search

### Task: Find Specific Datasets
**Use Case**: You know what kind of data you're looking for but not the exact dataset name.

**Recommended Tools**:
1. `ckan_package_search` — Primary tool for discovery
   - Search by keywords: `q="climate data"`
   - Filter by organization: `fq="organization:environmental-dept"`
   - Filter by format: `fq="res_format:CSV"`
   - Sort by relevance: `sort="score desc"`

**Example Flow**:
```
User: "Find all climate-related datasets published by the Environmental Department"
Tool Call 1: ckan_package_search(q="climate", fq="organization:environmental-dept", rows=20)
Result: Returns 15 datasets with titles, descriptions, and resource URLs
User: "Show me details for the top result"
Tool Call 2: ckan_package_show(id="climate-observations-2024")
Result: Full metadata including all resources, dates, maintainer info
```

### Task: Browse All Datasets
**Use Case**: You want a complete inventory of datasets without searching.

**Recommended Tools**:
1. `ckan_package_list` — Paginate through all datasets
   - Use `limit` and `offset` for pagination (100 at a time)

**Example Flow**:
```
Tool Call: ckan_package_list(limit=50, offset=0)
Result: First 50 datasets
Tool Call: ckan_package_list(limit=50, offset=50)
Result: Next 50 datasets (continue paging as needed)
```

### Task: Explore by Organization
**Use Case**: Find datasets published by a specific team or department.

**Recommended Tools**:
1. `ckan_organization_list` — List all organizations
2. `ckan_organization_show` — View organization details + datasets
3. `ckan_package_search` — Filter search results by org

**Example Flow**:
```
Tool Call 1: ckan_organization_list(all_fields=True)
Result: All departments/orgs with descriptions
Tool Call 2: ckan_organization_show(id="health-department", include_datasets=True)
Result: All datasets published by Health Department, plus contact info
```

### Task: Understand Data Taxonomy
**Use Case**: Learn about tags, themes, and how data is organized.

**Recommended Tools**:
1. `ckan_tag_list` — Browse all tags used in the portal
2. `ckan_group_list` — Browse themed data groups/categories
3. `ckan_package_search` — Filter by tags or groups

**Example Flow**:
```
Tool Call 1: ckan_tag_list()
Result: All available tags (e.g., "open-data", "transportation", "census")
Tool Call 2: ckan_package_search(fq="tags:transportation", rows=50)
Result: All transportation-tagged datasets
```

---

## 📊 Data Access & Analysis

### Task: Query Structured Data
**Use Case**: You need to access actual data values, apply filters, sort, and analyze without downloading.

**Recommended Tools**:
1. `ckan_resource_show` — Check resource metadata first
2. `ckan_datastore_search` — Query table data with filters and sorting

**Example Flow**:
```
Tool Call 1: ckan_resource_show(id="resource-uuid-123")
Result: Resource metadata (format, size, creation date, description)
Tool Call 2: ckan_datastore_search(
    resource_id="resource-uuid-123",
    q="department=Finance",  # Full-text search
    sort="date desc",
    limit=100
)
Result: First 100 matching records sorted by date
```

**Use Cases for DataStore Search**:
- Filter records: `q="status=completed"`
- Sort results: `sort="amount desc"` to find highest values
- Pagination: Use `offset` to navigate large datasets
- Column selection: Specify `fields` to get only needed columns

### Task: Download Data for Local Analysis
**Use Case**: You want to download a dataset to your computer for analysis, visualization, or archival.

**Recommended Tools**:
1. `ckan_package_search` or `ckan_package_show` — Find the dataset
2. `ckan_resource_show` — Check resource details (format, size)
3. `ckan_resource_download` — Download the file

**Example Flow**:
```
Tool Call 1: ckan_package_show(id="budget-2024")
Result: Dataset info with 3 resources (CSV, JSON, Excel)
Tool Call 2: ckan_resource_show(id="resource-456")
Result: Resource metadata shows it's 50MB CSV file
Tool Call 3: ckan_resource_download(
    resource_id="resource-456",
    output_folder="/home/user/downloads",
    output_format="file"
)
Result: File saved to /home/user/downloads/budget-2024-detail.csv
```

**Output Format Options**:
- `file` — Save resource to disk (for binary/large files)
- `json` — Parse and return as JSON object (for structured data)
- `raw` — Return metadata only (check before downloading)

---

## 🏢 Organizational Reporting

### Task: Generate Organization Report
**Use Case**: Create a report showing all datasets published by an organization, including metadata and statistics.

**Recommended Tools**:
1. `ckan_organization_show` — Get org info + all datasets (if `include_datasets=True`)
2. `ckan_site_read` — Get portal-wide statistics for context

**Example Flow**:
```
Tool Call 1: ckan_organization_show(id="data-governance-team", include_datasets=True)
Result: 
  - Organization name, description, member count
  - List of 42 published datasets with titles, IDs, update dates
Tool Call 2: ckan_site_read()
Result: Portal has 1,200 total datasets, 35 organizations
```

### Task: Monitor Recently Updated Datasets
**Use Case**: Find datasets that have been updated recently for quality checks or news.

**Recommended Tools**:
1. `ckan_package_search` — Sort by modification date

**Example Flow**:
```
Tool Call: ckan_package_search(
    q="*:*",
    sort="metadata_modified desc",
    rows=20
)
Result: 20 most recently updated datasets
User: "Show details for the newest one"
Tool Call 2: ckan_package_show(id="top-recent-id")
Result: Full metadata with update timestamp
```

---

## 🔧 System Administration

### Task: Check Portal Health
**Use Case**: Verify that the CKAN instance is running and responsive.

**Recommended Tools**:
1. `ckan_status_show` — Check system status and version
2. `ckan_site_read` — Get portal statistics

**Example Flow**:
```
Tool Call 1: ckan_status_show()
Result: {"system": "ok", "version": "2.10.1"}
Tool Call 2: ckan_site_read()
Result: Portal statistics (datasets, orgs, groups, etc.)
```

### Task: Get Portal Information
**Use Case**: Display portal name, description, and aggregate statistics on a dashboard.

**Recommended Tools**:
1. `ckan_site_read` — Get portal metadata and stats

**Example Flow**:
```
Tool Call: ckan_site_read()
Result:
  - Site name and description
  - Total datasets: 1,200
  - Total organizations: 35
  - Total groups: 8
  - Total tags: 450
```

---

## 📋 Data Inventory & Governance

### Task: Create a Data Inventory
**Use Case**: Document all datasets, their formats, organizations, and creation dates for governance purposes.

**Recommended Tools**:
1. `ckan_package_list` — Get all datasets with pagination
2. `ckan_package_show` — Get full details for each dataset
3. OR `ckan_package_search` with `rows=1000` — Get large batch in one call

**Example Flow**:
```
Step 1: Get all datasets
Tool Call 1: ckan_package_search(q="*:*", rows=1000)
Result: All datasets (or first 1000)

Step 2: For detailed report, loop through each
For each dataset_id in results:
  Tool Call: ckan_package_show(id=dataset_id)
  Result: Full metadata for export to inventory file

Step 3: Create inventory
- Extract: ID, title, org, creation date, update date, resource count, format types
- Export to spreadsheet for governance team
```

### Task: Identify Dataset Quality Issues
**Use Case**: Find datasets missing descriptions, outdated resources, or other quality problems.

**Recommended Tools**:
1. `ckan_package_list` or `ckan_package_search` — Get datasets
2. `ckan_package_show` — Check individual dataset metadata for quality indicators

**Quality Checks**:
- Missing description: `dataset.notes == ""`
- Outdated resources: `resource.last_modified` > 2 years ago
- Missing format info: `resource.format == ""`
- No maintainer contact: `dataset.maintainer == ""`

---

## 🎯 Common Query Patterns

### Pattern: Exclude Private Datasets
```
ckan_package_search(
    q="climate",
    include_private=False  # Only public datasets
)
```

### Pattern: Multiple Filters
```
ckan_package_search(
    q="health",
    fq="organization:health-dept AND res_format:CSV",
    sort="score desc"
)
```

### Pattern: Paginate Large Result Sets
```
# First page
ckan_package_search(q="*:*", rows=100, start=0)

# Second page
ckan_package_search(q="*:*", rows=100, start=100)

# Continue: start=200, 300, 400, etc.
```

### Pattern: Get Only Specific Resource Columns
```
ckan_datastore_search(
    resource_id="resource-id",
    fields=["date", "amount", "category"],  # Only these columns
    limit=1000
)
```

### Pattern: Find Newest Datasets
```
ckan_package_search(
    q="*:*",
    sort="metadata_created desc",  # Newest first
    rows=20
)
```

### Pattern: Find Most Recently Modified Datasets
```
ckan_package_search(
    q="*:*",
    sort="metadata_modified desc",  # Recently updated
    rows=20
)
```

---

## 📌 Quick Reference Table

| Task | Primary Tool | Supporting Tools |
|------|--------------|------------------|
| Find datasets | `ckan_package_search` | `ckan_package_show` |
| Browse all | `ckan_package_list` | — |
| Get dataset details | `ckan_package_show` | — |
| Access table data | `ckan_datastore_search` | `ckan_resource_show` |
| Download file | `ckan_resource_download` | `ckan_resource_show` |
| Organization info | `ckan_organization_show` | `ckan_organization_list` |
| Explore taxonomy | `ckan_tag_list`, `ckan_group_list` | `ckan_package_search` |
| Portal health | `ckan_status_show` | `ckan_site_read` |
| Portal stats | `ckan_site_read` | — |

---

## 💡 Tips for LLM Integration

### For Data Analysts
1. **Start with search**, not list — search is more targeted
2. **Use filters** (`fq`) to narrow down results before fetching full details
3. **Check metadata first** — use `ckan_resource_show` before downloading to check file size

### For Developers
1. **Handle pagination** — CKAN may return partial results; use `offset` to fetch all
2. **Validate resource IDs** — resources and packages have different ID types
3. **Check resource format** — before trying to parse, verify format matches expected type

### For Data Governance Teams
1. **Use `include_datasets=True`** in organization queries for complete org reports
2. **Combine searches** with filters to build compliance reports
3. **Monitor update dates** — `metadata_modified` field tracks when datasets change

