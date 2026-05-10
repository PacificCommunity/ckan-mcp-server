# CKAN MCP Tool Capabilities Reference

This document provides a structured overview of all available tools, organized by capability domain for easy discovery and understanding.

---

## 📊 Tool Groups

CKAN MCP Server tools are organized into 5 capability domains:

1. **Data Discovery & Search** — Find and explore datasets
2. **Data Access & Retrieval** — Access and download data
3. **Organization & Structure** — Navigate portals and taxonomies
4. **System & Status** — Monitor portal health and metadata

---

## 🔍 GROUP 1: DATA DISCOVERY & SEARCH

**Purpose**: Find datasets by searching, browsing, or filtering.

### ckan_package_search
**Capability**: Full-text search with filtering and sorting  
**Task**: Find specific datasets by content, keywords, tags, or metadata  
**Key Parameters**:
- `q` - Search keywords (e.g., "climate", "budget")
- `fq` - Advanced filter (e.g., "organization:health", "res_format:CSV")
- `sort` - Ranking (e.g., "score desc", "metadata_modified desc")
- `rows` - Results per page (1-1000)

**Best For**:
- ✅ Exploratory search for specific data
- ✅ Finding datasets by organization, format, or date
- ✅ Building filtered datasets for reporting
- ❌ Listing all datasets (use `ckan_package_list` instead)

**Example**: Search for environmental datasets updated in the last 30 days:
```
q="environment", sort="metadata_modified desc", rows=50
```

---

### ckan_package_list
**Capability**: Paginated listing of all datasets  
**Task**: Browse all available datasets without filtering  
**Key Parameters**:
- `limit` - Number to return per page (typically 100)
- `offset` - Pagination offset

**Best For**:
- ✅ Complete dataset inventory
- ✅ Data governance/auditing
- ✅ When you need to see everything
- ❌ When searching for specific data (use `ckan_package_search`)

**Example**: Get all datasets in batches of 50:
```
limit=50, offset=0  (first 50)
limit=50, offset=50 (next 50)
limit=50, offset=100 (and so on)
```

---

## 📥 GROUP 2: DATA ACCESS & RETRIEVAL

**Purpose**: Access actual data records, retrieve metadata, and download files.

### ckan_package_show
**Capability**: Full dataset metadata retrieval  
**Task**: Get complete information about a specific dataset  
**Key Parameters**:
- `id` - Dataset ID or name

**Returns**:
- Title, description, creation/update dates
- All resources (files) with URLs and formats
- Maintainer and contact information
- Organization, groups, tags, licenses
- Complete dataset metadata

**Best For**:
- ✅ Getting full details after finding a dataset
- ✅ Understanding dataset structure before analysis
- ✅ Extracting resource IDs for downloading
- ✅ Building comprehensive dataset reports

**Example**: Get all metadata for "annual-budget-2024"
```
id="annual-budget-2024"
Returns: 5 resources (CSV, JSON, Excel, PDF, API)
```

---

### ckan_datastore_search
**Capability**: Query structured table data with filters and sorting  
**Task**: Access actual data values in tabular resources  
**Key Parameters**:
- `resource_id` - DataStore table ID
- `q` - Full-text search query
- `sort` - Column to sort by (e.g., "date desc")
- `limit` - Results per page
- `offset` - Pagination offset
- `fields` - Specific columns to retrieve

**Best For**:
- ✅ Analyzing data without downloading
- ✅ Filtering records (WHERE clauses)
- ✅ Sorting results by column
- ✅ Paginating through large datasets
- ❌ Non-tabular data (use `ckan_resource_download`)

**Example**: Find all high-value transactions sorted newest first:
```
resource_id="123-abc", q="amount>10000", sort="date desc", limit=100
```

---

### ckan_resource_show
**Capability**: Retrieve metadata about a specific resource (file)  
**Task**: Check resource details before downloading or accessing  
**Key Parameters**:
- `id` - Resource UUID

**Returns**:
- Resource URL and file format
- File size and creation date
- Last modified date
- Description and format details

**Best For**:
- ✅ Checking file size before downloading
- ✅ Verifying resource format compatibility
- ✅ Extracting direct download URLs
- ✅ Checking resource metadata/description

**Example**: Verify that a resource is a CSV file before attempting JSON parse:
```
id="resource-uuid-456"
Returns: format="CSV", size=15728640 bytes, url="http://..."
```

---

### ckan_resource_download
**Capability**: Download dataset files to local storage  
**Task**: Save dataset files for local analysis or archival  
**Key Parameters**:
- `resource_id` - Resource UUID
- `output_folder` - Local path where file will be saved
- `output_format` - How to return data:
  - `file` - Save to disk
  - `json` - Parse and return as JSON
  - `raw` - Return metadata only

**Best For**:
- ✅ Downloading datasets for offline analysis
- ✅ Archiving data files locally
- ✅ Getting data into your tools/systems
- ✅ Exporting data in different formats

**Example**: Download a CSV file to local storage:
```
resource_id="123-abc", output_folder="/home/user/data", output_format="file"
Returns: File saved as /home/user/data/dataset-name.csv
```

---

## 🏢 GROUP 3: ORGANIZATION & STRUCTURE

**Purpose**: Navigate organizational hierarchies, taxonomies, and data structure.

### ckan_organization_list
**Capability**: List all data-publishing organizations  
**Task**: Discover organizations and their basic info  
**Key Parameters**:
- `all_fields` - Include full details (names, descriptions, stats)

**Best For**:
- ✅ Understanding portal's organizational structure
- ✅ Finding which organization publishes specific data
- ✅ Organizational reporting
- ✅ Building org-based dashboards

**Example**: Get all organizations with details:
```
all_fields=True
Returns: List of 35 organizations (Health, Environmental, Transportation depts, etc.)
```

---

### ckan_organization_show
**Capability**: Get full details for a specific organization  
**Task**: Retrieve org info including contact data and all published datasets  
**Key Parameters**:
- `id` - Organization name or ID
- `include_datasets` - Include all datasets published by this org

**Returns** (with `include_datasets=True`):
- Organization name, description, contact info
- Image/logo URL
- All published datasets (IDs, titles, update dates)
- Member list and roles

**Best For**:
- ✅ Organization-specific reports
- ✅ Finding all datasets from a department
- ✅ Understanding data stewardship
- ✅ Contact and governance information

**Example**: Get all datasets from "Health Department":
```
id="health-dept", include_datasets=True
Returns: 23 published datasets + org metadata
```

---

### ckan_group_list
**Capability**: List all data groups/themes/categories  
**Task**: Discover how data is organized thematically  
**Key Parameters**:
- `all_fields` - Include descriptions and metadata

**Best For**:
- ✅ Understanding data taxonomy/categories
- ✅ Finding related datasets by theme
- ✅ Building themed data collections
- ✅ Portal structure documentation

**Example**: Explore data categories:
```
all_fields=True
Returns: Groups like "Transportation", "Health", "Environment", "Finance"
```

---

### ckan_tag_list
**Capability**: List all metadata tags/keywords used in portal  
**Task**: Discover available tags and controlled vocabularies  
**Key Parameters**:
- `vocabulary_id` - Filter to specific controlled vocabulary (optional)

**Best For**:
- ✅ Understanding tagging conventions
- ✅ Finding related tags
- ✅ Building tag-based searches
- ✅ Data cataloging and taxonomy work

**Example**: Get all tags related to datasets:
```
vocabulary_id=None (all tags)
Returns: 450+ tags (climate, health, budget, transportation, etc.)
```

---

## 🔧 GROUP 4: SYSTEM & STATUS

**Purpose**: Monitor portal health and retrieve system information.

### ckan_status_show
**Capability**: Check CKAN system status and version  
**Task**: Verify portal is running and identify version  
**Key Parameters**: None

**Returns**:
- System status (ok/error)
- CKAN version number
- API compatibility information

**Best For**:
- ✅ Health checks and monitoring
- ✅ Version compatibility verification
- ✅ Operational alerts
- ✅ Initial connection test

**Example**: Verify portal is available:
```
No parameters
Returns: {"system": "ok", "ckan_version": "2.10.1"}
```

---

### ckan_site_read
**Capability**: Get portal-wide metadata and statistics  
**Task**: Retrieve aggregate information about the entire portal  
**Key Parameters**: None

**Returns**:
- Portal name and description
- Total dataset count
- Total organization count
- Total group count
- Total tag count
- Portal homepage and metadata

**Best For**:
- ✅ Portal-level reporting and dashboards
- ✅ Data governance metrics
- ✅ Portal statistics for stakeholders
- ✅ Understanding portal scope

**Example**: Get portal statistics:
```
No parameters
Returns: 1,200 datasets, 35 organizations, 8 groups, 450 tags
```

---

## 🎯 Capability Matrix

| Capability | Tool | Input | Output | Use Case |
|-----------|------|-------|--------|----------|
| **Search** | `ckan_package_search` | Query + filters | 10-1000 datasets | Find specific data |
| **Browse** | `ckan_package_list` | Limit + offset | All datasets (paginated) | Inventory, audit |
| **Metadata** | `ckan_package_show` | Dataset ID | Full dataset info | Get details |
| **Query** | `ckan_datastore_search` | Resource ID + filters | Table data (paginated) | Analyze data online |
| **Resource** | `ckan_resource_show` | Resource ID | File metadata | Check before download |
| **Download** | `ckan_resource_download` | Resource ID + folder | File saved to disk | Get data locally |
| **Orgs** | `ckan_organization_show` | Org ID | Org info + datasets | Org reports |
| **Tags** | `ckan_tag_list` | Vocabulary ID | All tags | Understand taxonomy |
| **Status** | `ckan_status_show` | None | System status | Health check |
| **Stats** | `ckan_site_read` | None | Portal statistics | Reporting |

---

## 🔄 Typical Workflow Patterns

### Pattern 1: Search → Show → Download
```
1. ckan_package_search(q="climate")
   → Find datasets matching "climate"

2. ckan_package_show(id=<top_result>)
   → Get full details including resources

3. ckan_resource_download(resource_id=<resource_id>, output_folder="/home/user")
   → Save the data file locally
```

### Pattern 2: Organization → Details → Analyze
```
1. ckan_organization_list()
   → Find organization names

2. ckan_organization_show(id=<org_id>, include_datasets=True)
   → Get all datasets from organization

3. ckan_datastore_search(resource_id=<resource_id>, sort="date desc")
   → Analyze the data online
```

### Pattern 3: Browse → Query → Download
```
1. ckan_package_list(limit=50, offset=0)
   → Paginate through all datasets

2. ckan_package_show(id=<dataset_id>)
   → Get details for specific dataset

3. ckan_datastore_search(resource_id=<resource_id>, limit=100)
   → Query data records online
```

### Pattern 4: Portal Health Check
```
1. ckan_status_show()
   → Verify system is running

2. ckan_site_read()
   → Get portal statistics

Result: Can report "Portal OK, 1,200 datasets, 35 organizations"
```

---

## 💡 Decision Tree: Which Tool to Use?

```
Do you want to FIND datasets?
├─ Yes, with search → ckan_package_search (+ optional filters)
└─ No, browse all → ckan_package_list

Do you want FULL details about a dataset?
└─ Yes → ckan_package_show

Do you want to ACCESS the actual data?
├─ Yes, analyze online → ckan_datastore_search
└─ Yes, download → ckan_resource_download

Do you want ORGANIZATION information?
├─ List all → ckan_organization_list
└─ Details of one → ckan_organization_show

Do you want TAXONOMIC/STRUCTURAL info?
├─ Tags → ckan_tag_list
└─ Groups/themes → ckan_group_list

Do you want SYSTEM information?
├─ Status/health → ckan_status_show
└─ Statistics → ckan_site_read
```

---

## 📝 Notes for Different Audiences

### For Data Analysts
- Use `ckan_package_search` with specific filters for efficiency
- Use `ckan_datastore_search` to analyze before downloading
- Use `sort="metadata_modified desc"` to find newest/updated data

### For System Administrators
- Use `ckan_status_show` for operational monitoring
- Use `ckan_site_read` for reporting dashboards
- Use `ckan_organization_list` + `ckan_package_list` for audits

### For Data Governance Teams
- Use `ckan_organization_show(include_datasets=True)` for org reports
- Use `ckan_package_show` to verify metadata quality
- Use `ckan_package_search` to find quality issues (missing descriptions, etc.)

### For LLM/AI Integration
- All tools are designed for async operation
- Paginate results with `limit`/`offset` or `rows`/`start`
- Always check `ckan_status_show` first to verify connectivity
- Use semantic context: descriptions now tell you what to do, not just what the API does

