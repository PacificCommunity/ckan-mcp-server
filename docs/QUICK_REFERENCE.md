# CKAN MCP Tools Quick Reference Card

**For LLM Developers & AI Integration Specialists**

---

## 🚀 10-Second Tool Overview

| Domain | Tools | Use When |
|--------|-------|----------|
| **Search** | `ckan_package_search` | User asks "find datasets about X" |
| **Browse** | `ckan_package_list` | Need inventory of ALL datasets |
| **Details** | `ckan_package_show` | Need full info about a dataset |
| **Query** | `ckan_datastore_search` | Need to analyze data online |
| **Download** | `ckan_resource_download` | User wants data on their system |
| **Org Info** | `ckan_organization_show` | Need org's datasets + metadata |
| **Taxonomy** | `ckan_tag_list`, `ckan_group_list` | Explore data structure |
| **Health** | `ckan_status_show`, `ckan_site_read` | Check portal status/stats |

---

## 🎯 Common Flows (Copy-Paste Ready)

### "Find and Download Climate Data"
```
1. ckan_package_search(q="climate", sort="score desc", rows=10)
   → Gets top 10 climate datasets

2. ckan_package_show(id=<top_result_id>)
   → Gets all resources + metadata

3. ckan_resource_download(resource_id=<resource_id>, output_folder="/path", output_format="file")
   → Downloads the file
```

### "Get Organization's Latest Datasets"
```
1. ckan_organization_show(id="health-dept", include_datasets=True)
   → Gets all datasets from org

2. Sort results by metadata_modified desc
   → Latest first

3. ckan_package_show(id=<dataset_id>)
   → Get details for specific dataset
```

### "Check Portal Health"
```
1. ckan_status_show()
   → Verify system is running

2. ckan_site_read()
   → Get portal stats
```

### "Analyze Data Without Downloading"
```
1. ckan_datastore_search(resource_id=<resource_id>, limit=100, sort="date desc")
   → Query data online

2. Paginate: Use offset to get more results
   → offset=100, offset=200, etc.
```

---

## 🔍 Parameter Cheat Sheet

### Common Filter Patterns
```
# By organization
fq="organization:health-dept"

# By file format
fq="res_format:CSV"

# By creation date (past 30 days)
sort="metadata_created desc"

# By update date (most recent)
sort="metadata_modified desc"

# Combine filters
fq="organization:health AND res_format:JSON"
```

### Search Query Examples
```
q="climate"              # Keyword search
q="budget 2024"          # Multiple keywords
q="*:*"                  # All datasets
q=""                     # Empty search (use filters instead)
```

### DataStore Query Examples
```
sort="date desc"         # Most recent first
sort="amount desc"       # Highest values first
limit=100                # Get 100 records
fields=["date", "name"]  # Only specific columns
q="status=active"        # Text search
```

---

## ⚠️ Common Gotchas

| Issue | Solution |
|-------|----------|
| No results from search | Try `q="*:*"` with filters instead |
| DataStore search fails | Resource might not be in DataStore; use `ckan_resource_download` instead |
| Pagination not working | Use `rows`+`start` for search, `limit`+`offset` for datastore |
| Getting too many results | Add filters with `fq` to narrow down |
| Resource format unknown | Call `ckan_resource_show` first to check format |
| API slow on large results | Reduce `rows`/`limit` or use more specific filters |

---

## 🏗️ Tool Dependencies & Sequences

```
To get a file:
  ckan_package_search 
    → ckan_package_show 
    → ckan_resource_show (optional)
    → ckan_resource_download

To understand organization:
  ckan_organization_list
    → ckan_organization_show
    → ckan_package_show (for each dataset)

To explore portal:
  ckan_status_show (verify online)
    → ckan_site_read (get stats)
    → ckan_tag_list (explore taxonomy)
    → ckan_package_search (find data)
```

---

## 📊 Tool Grouping (For Mental Model)

**Search/Discovery** (Start here):
- ckan_package_search
- ckan_package_list

**Get Details** (After finding):
- ckan_package_show
- ckan_resource_show

**Access Data** (To use/download):
- ckan_datastore_search
- ckan_resource_download

**Understand Structure** (For navigation):
- ckan_organization_list/show
- ckan_group_list
- ckan_tag_list

**Monitor** (For status checks):
- ckan_status_show
- ckan_site_read

---

## 🎯 Decision Tree

```
User wants to...

→ FIND data?
    Use: ckan_package_search
    
→ BROWSE all data?
    Use: ckan_package_list
    
→ GET full details?
    Use: ckan_package_show
    
→ ANALYZE data online?
    Use: ckan_datastore_search
    
→ DOWNLOAD file?
    Use: ckan_resource_download
    
→ GET ORG info?
    Use: ckan_organization_show
    
→ EXPLORE categories?
    Use: ckan_tag_list / ckan_group_list
    
→ CHECK status?
    Use: ckan_status_show / ckan_site_read
```

---

## 💾 Response Sizes (Approx)

| Tool | Response Size | Notes |
|------|---------------|-------|
| `ckan_package_search` | 50 KB-1 MB | Depends on `rows` param (10-1000) |
| `ckan_package_show` | 20-100 KB | Includes all resources + metadata |
| `ckan_datastore_search` | 10 KB-500 KB | Depends on `limit` and record size |
| `ckan_resource_download` | Variable | Depends on file size |
| `ckan_organization_show` | 50-500 KB | Depends on dataset count (if included) |
| `ckan_tag_list` | 20-100 KB | Usually ~100-500 tags |
| `ckan_status_show` | <1 KB | Very small |
| `ckan_site_read` | <10 KB | Summary statistics |

**Tip**: For memory-constrained LLMs, use smaller `rows`/`limit` values.

---

## 🔗 Links to Full Documentation

- **By Use Case**: Read `docs/TOOLS_BY_USE_CASE.md` for task-driven workflows
- **Capability Reference**: Read `docs/TOOL_CAPABILITIES.md` for detailed specs
- **Quick Examples**: See `docs/README.md` for example queries

---

## ✅ Pre-Integration Checklist

- [ ] CKAN_URL environment variable set
- [ ] CKAN_API_KEY set (or basic auth credentials)
- [ ] Test connectivity: Call `ckan_status_show()` first
- [ ] Read TOOLS_BY_USE_CASE.md for your specific use case
- [ ] Note any pagination requirements for your scenario
- [ ] Plan for large result sets (use filters to limit)

---

**Last Updated**: Phase 1 Complete  
**Version**: CKAN MCP Server 1.x  
**Audience**: LLM Developers & AI Integration Teams
