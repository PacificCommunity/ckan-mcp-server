# 5-Minute Quick Start for CKAN Admins

**Get CKAN MCP Server running in 5 minutes and start exploring your data with AI.**

> 🎯 **Goal**: Connect Claude (or any AI) to your CKAN portal so you can ask natural language questions about your data.

---

## ⏱️ 5-Minute Setup

### Step 1: Prerequisites (30 seconds)
You need:
- ✅ Python 3.13+ (check: `python --version`)
- ✅ Your CKAN URL (e.g., `https://demo.ckan.org`)
- ✅ API key from your CKAN account (optional, but recommended)

**Don't have an API key?**
1. Log in to your CKAN portal
2. Go to your user profile (top right)
3. Click "API Tokens" or "Settings"
4. Create a new API token
5. Copy it somewhere safe

### Step 2: Install (1 minute)
```bash
# Using pip
pip install ckan-mcp-server

# Or using uv (faster)
uv pip install ckan-mcp-server
```

### Step 3: Configure (1 minute)
Create a `.env` file in your home directory or project folder:

```bash
# .env file
CKAN_URL=https://your-ckan-portal.org
CKAN_API_KEY=your-api-key-here
```

**For Demo/Testing?**
```bash
CKAN_URL=https://demo.ckan.org
# No API key needed for public data
```

### Step 4: Start the Server (30 seconds)
```bash
# Direct
ckan-mcp-server

# Or with Python
python -m src.mcp_ckan_server

# Or with uv
uv run ckan-mcp-server
```

✅ **That's it!** Server is now running locally on stdio transport.

### Step 5: Connect to Claude (1.5 minutes)
**Option A: Claude Desktop (Recommended)**

1. Open Claude Desktop settings
2. Find `claude_desktop_config.json`:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

3. Add this to the `mcpServers` section:
```json
{
  "mcpServers": {
    "ckan": {
      "command": "ckan-mcp-server",
      "env": {
        "CKAN_URL": "https://your-ckan-portal.org",
        "CKAN_API_KEY": "your-api-key"
      }
    }
  }
}
```

4. Restart Claude Desktop
5. Look for 🔌 plug icon next to message bar → confirm tools are available

**Option B: Other LLM Clients** (VSCode, etc.)

Follow your client's MCP server documentation. Usually involves:
- Setting the command to `ckan-mcp-server`
- Passing environment variables for config

---

## 🎉 You're Done!

### First Steps with Claude

**In Claude, ask things like:**
- "Find me all climate-related datasets"
- "Show me the latest datasets from the Health Department"
- "Download the CSV file from the Transportation dataset"
- "What datasets were updated this week?"
- "List all organizations in the portal"

Claude will use the MCP tools automatically! 🤖

---

## 🔧 Troubleshooting

### Problem: "Command not found: ckan-mcp-server"

**Solution**: Install globally or use Python module:
```bash
# Option 1: Install with --user flag
pip install --user ckan-mcp-server
# Then add to PATH or use: python -m src.mcp_ckan_server

# Option 2: Use Python directly
python -m src.mcp_ckan_server
```

### Problem: "Connection refused" or "Cannot reach CKAN"

**Solution**: Check your CKAN_URL
```bash
# Test if your CKAN is accessible
curl -I https://your-ckan-portal.org/api/3/action/status_show

# If that fails, CKAN might be:
# - Down (check with your IT team)
# - Behind a firewall (check network access)
# - Using self-signed SSL cert (add CA certificate to certifi)
```

### Problem: "API Key invalid" or "Unauthorized"

**Solution**: Verify your API key
```bash
# Check if API key works
curl -H "Authorization: <your-api-key>" \
  https://your-ckan-portal.org/api/3/action/package_list

# If error, re-generate your API key in CKAN
```

### Problem: Claude can't find the tools

**Solution**: Check Claude Desktop config
1. Verify JSON syntax (use jsonlint.com)
2. Restart Claude Desktop completely
3. Check logs:
   - macOS: `~/Library/Logs/Claude Desktop/`
   - Check stderr output from server

### Problem: Server crashes or gets stuck

**Solution**: Restart with debug output
```bash
# Enable verbose logging
ckan-mcp-server --loglevel DEBUG

# Check output for error messages
# Common issues:
# - CKAN server down
# - Network timeout (large dataset query)
# - Invalid resource ID
```

---

## 📚 Next Steps

### Learn More
- **Task-based guide**: Read [Tools by Use Case](./TOOLS_BY_USE_CASE.md)
- **Technical reference**: Read [Tool Capabilities](./TOOL_CAPABILITIES.md)
- **Quick lookups**: Use [Quick Reference](./QUICK_REFERENCE.md)

### Common Tasks for CKAN Admins

**1. Monitor Dataset Health**
```
Ask Claude: "Show me all datasets that haven't been updated in 30 days"
→ Claude will search and alert you to stale data
```

**2. Create Organization Reports**
```
Ask Claude: "Get all datasets from the Finance Department with their update dates"
→ Claude will compile org-specific inventory
```

**3. Find Missing Metadata**
```
Ask Claude: "List datasets without descriptions or with no resources"
→ Claude will identify quality issues
```

**4. Export Data Inventory**
```
Ask Claude: "Create a CSV of all datasets, organizations, and formats"
→ Claude can compile reports for governance
```

**5. Explore Data Portal Structure**
```
Ask Claude: "What are the main categories and themes in this portal?"
→ Claude will show tags, groups, and organization structure
```

---

## 🔐 Security Notes

✅ **API keys** are read-only for most CKAN instances  
✅ **Credentials** stay on your machine (not shared with Anthropic)  
✅ **HTTPS** used for all API calls  
✅ **SSL certificates** verified via certifi  

**Best Practice**: Create a read-only API key in CKAN for this purpose.

---

## 💬 Getting Help

- **Setup issues**: Check [Troubleshooting](#-troubleshooting) above
- **Tool questions**: Read [Tools by Use Case](./TOOLS_BY_USE_CASE.md)
- **Technical issues**: Check logs with `--loglevel DEBUG`
- **Feature requests**: Open an issue on GitHub

---

## 📋 Quick Checklist

- [ ] Python 3.13+ installed
- [ ] CKAN URL and API key noted
- [ ] `pip install ckan-mcp-server` completed
- [ ] `.env` file configured
- [ ] Server starts without errors
- [ ] Claude Desktop config updated
- [ ] Tools showing in Claude
- [ ] First query works!

**That's it! You're ready to use AI-powered data exploration.** 🚀

---

**Next**: Ready to dive deeper? Check out [Scenario Examples](./SCENARIO_EXAMPLES.md) for real-world use cases.
