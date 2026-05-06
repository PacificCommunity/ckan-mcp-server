# Real-World Scenarios: CKAN MCP in Action

**Practical examples of using CKAN MCP Server with Claude for common data management tasks.**

---

## 📊 Scenario 1: Find Recently Updated Datasets

**Situation**: You're a data governance officer who needs to know which datasets have been updated recently.

**Ask Claude:**
> "Show me the 10 most recently updated datasets in our portal"

**What Claude Does**:
1. Calls `ckan_package_search(sort="metadata_modified desc", rows=10)`
2. Displays dataset titles, organizations, and update dates
3. You can ask follow-up questions

**Example Output**:
```
Recent Updates (Last Modified):
1. Budget Report 2024 (Finance Dept)      - Updated: 2026-05-05
2. Traffic Statistics Q1 2026 (Transport) - Updated: 2026-05-03
3. Vaccination Records (Health)           - Updated: 2026-05-02
4. Environmental Survey (Environment)     - Updated: 2026-05-01
...
```

**Follow-up Questions**:
- "Get the actual data from the Budget Report"
- "Which organization hasn't updated their datasets recently?"
- "Download the traffic statistics file"

**Why This Matters**: Staying on top of data freshness is critical for trust and compliance.

---

## 🏢 Scenario 2: Generate Organization Report

**Situation**: The Health Department director asks you for a report of all datasets their organization has published.

**Ask Claude:**
> "Get all datasets published by the Health Department and show me their titles, creation dates, and formats"

**What Claude Does**:
1. Calls `ckan_organization_show(id="health-department", include_datasets=True)`
2. Extracts dataset information
3. Formats it into a readable report
4. Optionally exports as CSV/JSON

**Example Output**:
```
Health Department Dataset Inventory:
┌─────────────────────────────────┬──────────────┬─────────────┐
│ Dataset Title                   │ Created      │ Formats     │
├─────────────────────────────────┼──────────────┼─────────────┤
│ Vaccination Records 2024        │ 2024-01-15   │ CSV, JSON   │
│ Hospital Capacity Reports       │ 2024-02-01   │ CSV, Excel  │
│ Disease Surveillance Data       │ 2024-03-10   │ CSV, API    │
│ Clinical Trial Results          │ 2024-04-01   │ JSON, XML   │
└─────────────────────────────────┴──────────────┴─────────────┘

Total: 4 datasets published
```

**Why This Matters**: 
- Department heads need to know what they're publishing
- Useful for oversight and stewardship documentation
- Helps identify gaps in open data publishing

---

## 🔍 Scenario 3: Search by Organization and Format

**Situation**: You're looking for all CSV files published by Transportation Department for your analysis.

**Ask Claude:**
> "Find all CSV datasets from the Transportation Department"

**What Claude Does**:
1. Calls `ckan_package_search(fq="organization:transportation AND res_format:CSV", rows=50)`
2. Returns all matching datasets with download links
3. You can preview or download specific resources

**Example Output**:
```
Found 12 CSV datasets from Transportation:
1. Traffic Flow Data (2024)
   → traffic-flow-daily.csv (15 MB)
   
2. Transit Schedule Updates
   → bus-routes-2024.csv (2 MB)
   
3. Road Construction Projects
   → construction-status.csv (5 MB)
...
```

**Follow-up Actions**:
- "Download the traffic flow CSV"
- "Show me the first 100 rows of traffic data"
- "Compare with the 2023 version"

**Why This Matters**: Format-specific searches are essential when you need to process data in a particular way.

---

## 📥 Scenario 4: Download and Analyze Data

**Situation**: You need to analyze budget spending by category for a presentation.

**Ask Claude:**
> "Download the annual budget dataset and show me spending by category"

**What Claude Does**:
1. Finds the budget dataset via `ckan_package_search`
2. Gets resource details via `ckan_resource_show`
3. Downloads the file via `ckan_resource_download`
4. Analyzes the data (if possible) or prepares for your analysis

**Example Workflow**:
```
Claude: "I found the Annual Budget 2024 dataset. 
        It has a CSV file (8 MB) with spending data.
        Downloading now..."

[File saved to: ~/Downloads/annual-budget-2024.csv]

Claude: "Preview of the data:
Category        Amount       Percentage
Healthcare      $500M        35%
Education       $400M        28%
Infrastructure  $300M        21%
Other           $200M        14%"
```

**Why This Matters**: Combines search, download, and analysis in one conversational flow.

---

## 🏥 Scenario 5: Find Datasets by Theme/Tag

**Situation**: You're building a climate change awareness initiative and need all climate-related datasets.

**Ask Claude:**
> "Find all datasets tagged with 'climate' or 'environment'"

**What Claude Does**:
1. Searches via `ckan_package_search(q="climate OR environment", rows=100)`
2. Filters to those with relevant tags
3. Organizes by organization
4. Suggests related datasets

**Example Output**:
```
🌍 Climate & Environment Datasets (23 found):

By Organization:
├─ Environmental Protection Agency (8 datasets)
│  ├─ Air Quality Monitoring
│  ├─ Carbon Emissions Inventory
│  └─ ...
├─ Weather Bureau (6 datasets)
│  ├─ Temperature Records
│  ├─ Precipitation Data
│  └─ ...
└─ University Research (5 datasets)
   └─ ...

Related Tags: climate, environment, weather, pollution, emissions
```

**Why This Matters**: Theme-based discovery helps identify related datasets for comprehensive analysis.

---

## 📋 Scenario 6: Audit Dataset Quality

**Situation**: Your compliance team needs to verify that all datasets have proper descriptions and current maintainers.

**Ask Claude:**
> "Check all datasets for quality issues: missing descriptions, no maintainer info, or resources older than 1 year"

**What Claude Does**:
1. Lists all datasets via `ckan_package_list`
2. Checks each one for metadata completeness
3. Flags quality issues
4. Generates a compliance report

**Example Output**:
```
📊 Quality Audit Report

✅ Compliant Datasets: 45/50 (90%)

⚠️  Issues Found:

MISSING DESCRIPTIONS (3 datasets):
• Dataset ID: transportation-network
• Dataset ID: utility-billing-data
• Dataset ID: parking-locations

UNMAINTAINED RESOURCES (5 datasets):
• Population Census (last update: 2020-01-01) - STALE
• Historic Property Listings (last update: 2019-06-15) - VERY STALE
• ...

NO MAINTAINER CONTACT (2 datasets):
• Legacy Archive 1
• Legacy Archive 2
```

**Why This Matters**: Data governance requires regular audits of data quality and currency.

---

## 🔄 Scenario 7: Monitor Organization Performance

**Situation**: You manage multiple departments and want to see which organizations are most actively publishing data.

**Ask Claude:**
> "Show me all organizations ranked by number of datasets they've published"

**What Claude Does**:
1. Lists all organizations via `ckan_organization_list`
2. Gets dataset counts for each
3. Ranks by publishing activity
4. Highlights trends

**Example Output**:
```
📈 Organization Publishing Activity

🥇 Health Department          | 34 datasets | Last update: 2 days ago
🥈 Finance Department         | 28 datasets | Last update: 1 week ago
🥉 Transportation Authority   | 22 datasets | Last update: 5 days ago
4️⃣  Environmental Protection | 18 datasets | Last update: 2 weeks ago
5️⃣  Education Board           | 15 datasets | Last update: 3 weeks ago
❌ Parks Department           | 2 datasets  | Last update: 6 months ago

Insight: Parks Dept has low publishing activity - follow up?
```

**Why This Matters**: Identify which departments need encouragement or support with open data.

---

## 🎯 Scenario 8: Quick Portal Overview

**Situation**: New stakeholder asks "What's in our open data portal?"

**Ask Claude:**
> "Give me a 30-second overview of our CKAN portal"

**What Claude Does**:
1. Calls `ckan_site_read()` for aggregate stats
2. Calls `ckan_status_show()` for system health
3. Provides executive summary

**Example Output**:
```
🏛️  Portal Overview

System Status: ✅ Operational (CKAN 2.10.1)

📊 By The Numbers:
• Total Datasets: 1,247
• Organizations: 35
• Data Themes: 8
• Total Tags: 450
• Recent Updates: 12 this week

🏆 Top Publishers:
1. Health Department (34 datasets)
2. Finance Department (28 datasets)
3. Transportation (22 datasets)

📈 Growth: 45 new datasets this month
```

**Why This Matters**: Quick dashboard view for executives and new users.

---

## 🔗 Scenario 9: Cross-Organization Analysis

**Situation**: You're analyzing climate adaptation initiatives across multiple agencies.

**Ask Claude:**
> "Find all datasets related to climate adaptation from every organization"

**What Claude Does**:
1. Searches across portal with filters
2. Organizes by organization
3. Identifies collaboration opportunities
4. Suggests data connections

**Example Output**:
```
🌍 Climate Adaptation Datasets (by Organization)

HEALTH DEPT:
• Heat-Related Illness Trends
• Vulnerable Population Maps

ENVIRONMENT DEPT:
• Sea Level Rise Projections
• Flood Risk Areas

URBAN PLANNING:
• Climate Resilience Infrastructure
• Green Space Mapping

🔗 Collaboration Opportunities:
Could combine Heat-Related Illness + Vulnerable Population + Heat Risk Areas
for comprehensive climate health assessment
```

**Why This Matters**: Cross-organization analysis reveals systemic insights.

---

## 💾 Scenario 10: Data Export for Analysis

**Situation**: You need to export datasets for use in a PowerBI dashboard.

**Ask Claude:**
> "Get me the environmental monitoring data and export it as JSON for my analytics tool"

**What Claude Does**:
1. Finds the dataset
2. Downloads with `ckan_resource_download(output_format="json")`
3. Validates format
4. Provides integration guidance

**Example Output**:
```
📊 Exporting Environmental Monitoring Data

Source: Monthly Air Quality Index
Format: JSON
Size: 2.3 MB

Sample Record:
{
  "date": "2026-05-06",
  "location": "Downtown Station",
  "aqi": 78,
  "pm25": 45,
  "no2": 32,
  "o3": 125
}

✅ Ready to import into PowerBI
```

**Why This Matters**: Seamless integration between CKAN and analytics tools.

---

## 🎓 Key Takeaways

### When to Use What

| Need | Ask Claude | Tool Used |
|------|-----------|-----------|
| Find specific data | "Search for [topic]" | `ckan_package_search` |
| List everything | "Show all datasets" | `ckan_package_list` |
| Org inventory | "All datasets from [org]" | `ckan_organization_show` |
| Get actual data | "Download [dataset]" | `ckan_resource_download` |
| Check health | "Portal status" | `ckan_status_show` |
| Full details | "Details for [dataset]" | `ckan_package_show` |

### Pro Tips

✅ **Be specific** — "Climate datasets from 2023" better than "climate stuff"  
✅ **Use organization names** — Helps Claude find org-specific data  
✅ **Ask follow-ups** — Claude remembers context (e.g., "download it" after search)  
✅ **Request formats** — "Show as table", "export as CSV", "give me raw JSON"  
✅ **Combine questions** — "Find and download" works in one query  

---

## 📚 Learn More

- **Setup guide**: [Quick Start for Admins](./QUICK_START_ADMIN.md)
- **All available tools**: [Tool Capabilities](./TOOL_CAPABILITIES.md)
- **Detailed reference**: [Tools by Use Case](./TOOLS_BY_USE_CASE.md)

---

**Next**: Ready to set it up? Go to [Quick Start Guide](./QUICK_START_ADMIN.md) 🚀
