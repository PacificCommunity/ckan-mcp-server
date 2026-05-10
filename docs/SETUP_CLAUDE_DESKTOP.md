# Claude Desktop Integration Guide

**Step-by-step instructions to connect CKAN MCP Server to Claude Desktop.**

> By the end of this guide, you'll have AI-powered data exploration in Claude! 🤖

---

## 🎯 Overview

Claude Desktop is Anthropic's native AI application that supports Model Context Protocol (MCP) servers. This guide shows you exactly how to connect CKAN MCP Server so Claude can access your data portal.

**What You'll Be Able to Do**:
- Ask Claude to search your CKAN portal
- Download datasets directly from Claude
- Get analyses of your data
- Explore your portal structure naturally

---

## 📋 Prerequisites

Before starting, ensure you have:

1. **Claude Desktop installed**
   - Download from [claude.ai](https://claude.ai) → Desktop app
   - Or via Homebrew: `brew install --cask claude`

2. **CKAN MCP Server installed**
   ```bash
   pip install ckan-mcp-server
   # Verify: ckan-mcp-server --help
   ```

3. **CKAN credentials**
   - CKAN_URL: Your CKAN portal URL (e.g., `https://data.example.org`)
   - CKAN_API_KEY: (Optional) Your API key from CKAN

4. **Text editor**
   - Any editor will work (VS Code, Notepad, TextEdit, etc.)

---

## 🔧 Step 1: Locate Claude Desktop Config File

The config file location depends on your operating system.

### macOS
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Quick way**: Open Terminal and run:
```bash
open ~/Library/Application\ Support/Claude/
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Quick way**: 
1. Press `Win + R`
2. Type: `%APPDATA%\Claude\`
3. Press Enter

### Linux
```bash
~/.config/Claude/claude_desktop_config.json
```

**Quick way**:
```bash
cat ~/.config/Claude/claude_desktop_config.json
```

---

## 📝 Step 2: Edit the Config File

### If the file doesn't exist yet:

Create a new file with this content:

```json
{
  "mcpServers": {
    "ckan": {
      "command": "ckan-mcp-server",
      "env": {
        "CKAN_URL": "https://your-ckan-portal.org",
        "CKAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### If the file already exists:

Open it and add the `ckan` entry to the `mcpServers` section:

```json
{
  "mcpServers": {
    "ckan": {
      "command": "ckan-mcp-server",
      "env": {
        "CKAN_URL": "https://your-ckan-portal.org",
        "CKAN_API_KEY": "your-api-key-here"
      }
    },
    "other-server": {
      ...
    }
  }
}
```

---

## 🔑 Step 3: Configure Your CKAN Credentials

Edit the config values:

### Option A: With API Key (Recommended)
```json
{
  "mcpServers": {
    "ckan": {
      "command": "ckan-mcp-server",
      "env": {
        "CKAN_URL": "https://data.myorg.org",
        "CKAN_API_KEY": "ey-JhbGc..."
      }
    }
  }
}
```

**Get your API key**:
1. Log in to your CKAN portal
2. Go to your user profile (top right → My Name → Settings or API Tokens)
3. Create a new API token
4. Copy the entire token and paste it above

### Option B: With Basic Auth (Alternative)
```json
{
  "mcpServers": {
    "ckan": {
      "command": "ckan-mcp-server",
      "env": {
        "CKAN_URL": "https://data.myorg.org",
        "CKAN_BASIC_AUTH_USERNAME": "your-username",
        "CKAN_BASIC_AUTH_PASSWORD": "your-password"
      }
    }
  }
}
```

### Option C: Without Authentication (Public Portals)
```json
{
  "mcpServers": {
    "ckan": {
      "command": "ckan-mcp-server",
      "env": {
        "CKAN_URL": "https://demo.ckan.org"
      }
    }
  }
}
```

---

## ✅ Step 4: Save and Restart Claude

1. **Save the config file** (Ctrl+S / Cmd+S)
2. **Completely close Claude Desktop**
   - Make sure all Claude windows are closed
   - Check that it's not in the system tray
3. **Reopen Claude Desktop**
   - It should reconnect with the new configuration

---

## 🧪 Step 5: Verify Connection

### Look for the Tool Indicator

When Claude is connected to CKAN MCP Server, you'll see:
- **🔌 Plugin icon** next to the message input area (bottom right)
- **"Tools enabled"** message in the interface

### Test with a Simple Query

In Claude, ask:
> "Check the status of the CKAN portal"

**Expected Response**:
```
The CKAN portal is online and operational.
Status: OK
Version: 2.10.1
```

If Claude responds with portal information, you're connected! ✅

### If It Doesn't Work

See [Troubleshooting](#-troubleshooting) below.

---

## 🎓 Example Queries

Now try these to see Claude use your CKAN data:

### Example 1: Search Datasets
> "Find all datasets about climate in our portal"

Claude will:
1. Search your CKAN for climate-related datasets
2. List them with descriptions
3. Offer to help with follow-ups

### Example 2: Download Data
> "Download the transportation budget dataset to my computer"

Claude will:
1. Find the dataset
2. Download the file
3. Confirm where it was saved

### Example 3: Organization Info
> "Show me all datasets from the Finance Department"

Claude will:
1. Query the organization
2. List all published datasets
3. Show update dates and formats

### Example 4: Portal Health
> "Is our data portal healthy? Show me statistics"

Claude will:
1. Check system status
2. Get portal statistics
3. Give you an overview

---

## 🛠️ Troubleshooting

### Problem: "No tools available" or plugin icon missing

**Solution 1**: Verify config file syntax
```bash
# macOS/Linux: Validate JSON
python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# If it shows errors, check for:
# - Missing quotes around keys/values
# - Missing commas between entries
# - Mismatched braces
```

**Solution 2**: Check that server can run
```bash
# Test if ckan-mcp-server starts
ckan-mcp-server --help

# If command not found, reinstall
pip install --upgrade ckan-mcp-server
```

**Solution 3**: Restart Claude completely
- Close all Claude windows
- Check system tray (may be minimized)
- Open Activity Monitor (macOS) or Task Manager (Windows)
- Force quit any Claude processes
- Reopen Claude

### Problem: "Connection error" or "Cannot reach CKAN"

**Solution 1**: Verify CKAN_URL
```bash
# Test if your CKAN is accessible
curl -I https://your-ckan-portal.org/api/3/action/status_show

# Should return: HTTP/1.1 200 OK (or 401 if auth required)
```

**Solution 2**: Check API key if used
```bash
# Test API key
curl -H "Authorization: <your-api-key>" \
  https://your-ckan-portal.org/api/3/action/package_list

# Should return dataset information
```

**Solution 3**: Check network/firewall
- Can you access CKAN in a browser? Yes → Network OK
- If not, check with your IT team for:
  - Firewall rules blocking CKAN
  - VPN requirements
  - Proxy configuration needed

### Problem: "Invalid API key" or "Unauthorized"

**Solution 1**: Regenerate your API key
1. Log in to CKAN portal
2. Go to Settings → API Tokens
3. Delete old token
4. Create new token
5. Copy and paste into config

**Solution 2**: Check for trailing spaces
```json
"CKAN_API_KEY": "your-key-here "  // ❌ Space at end!
"CKAN_API_KEY": "your-key-here"   // ✅ Correct
```

### Problem: Tools work but queries are slow

**Common Causes**:
- CKAN server is slow (check with IT)
- Network latency (try different times)
- Large result sets (Claude is processing)

**Solutions**:
- Use more specific search queries
- Limit results: "Show me the first 5 datasets"
- Try simpler queries first

### Problem: "JSON parsing error" in config

**Solution**: Validate your config
```json
// ❌ WRONG - Missing quote
"mcpServers": {
  "ckan: {

// ✅ CORRECT - Proper quotes
"mcpServers": {
  "ckan": {
```

Use an online JSON validator: [jsonlint.com](https://www.jsonlint.com/)

---

## 🔐 Security Best Practices

### 1. API Key Safety
✅ **DO**:
- Use dedicated API keys for MCP
- Regenerate keys regularly
- Use read-only permissions if possible

❌ **DON'T**:
- Share API keys in messages
- Commit config file to git (if it has keys)
- Use your personal user account credentials

### 2. File Permissions (Linux/macOS)
```bash
# Make config readable only by you
chmod 600 ~/.config/Claude/claude_desktop_config.json
```

### 3. If You Share Your Computer
- Create a separate CKAN account for MCP
- Use basic auth instead of API keys (more trackable)
- Log out of Claude when not in use

---

## 📚 Advanced Configuration

### Multiple CKAN Instances

Need to connect to multiple CKAN portals?

```json
{
  "mcpServers": {
    "ckan-prod": {
      "command": "ckan-mcp-server",
      "env": {
        "CKAN_URL": "https://production.data.org",
        "CKAN_API_KEY": "prod-key-here"
      }
    },
    "ckan-dev": {
      "command": "ckan-mcp-server",
      "env": {
        "CKAN_URL": "https://development.data.org",
        "CKAN_API_KEY": "dev-key-here"
      }
    }
  }
}
```

Then ask Claude:
> "Using ckan-prod, find all health datasets"

### Custom Port or Path

If you need to run the server differently:

```json
{
  "mcpServers": {
    "ckan": {
      "command": "python",
      "args": ["-m", "src.mcp_ckan_server"],
      "env": {
        "CKAN_URL": "https://data.example.org",
        "CKAN_API_KEY": "your-key"
      }
    }
  }
}
```

---

## ❓ FAQ

**Q: Do I need an API key?**  
A: For public CKAN portals, no. For private data or write access, yes.

**Q: Is my data sent to Anthropic?**  
A: No. The MCP server runs on your machine. Only Claude (which runs locally in desktop) sees the data.

**Q: Can I use this with Claude.ai (web version)?**  
A: Not directly. MCP is currently desktop-only. Use the web version for basic questions about your data.

**Q: What if my CKAN is behind a firewall?**  
A: As long as you can access it from your computer, it should work. Check with your IT team if you get connection errors.

**Q: Can other apps connect to CKAN MCP Server?**  
A: Yes! Any MCP-compatible client can use it (VSCode, etc.). Follow similar config steps for other clients.

---

## 🎉 You're All Set!

Your Claude Desktop is now connected to CKAN. Start exploring your data! 🚀

### Next Steps

1. **Try the examples** in [Scenario Examples](./SCENARIO_EXAMPLES.md)
2. **Learn all tools** in [Tool Capabilities](./TOOL_CAPABILITIES.md)
3. **Get quick answers** from [Quick Reference](./QUICK_REFERENCE.md)

---

## 📞 Need Help?

- **Setup issues**: See [Troubleshooting](#-troubleshooting) above
- **How to use tools**: Read [Tools by Use Case](./TOOLS_BY_USE_CASE.md)
- **Technical details**: Check [Tool Capabilities](./TOOL_CAPABILITIES.md)

---

**Version**: Claude Desktop Integration Guide v1.0  
**Last Updated**: Phase 2 Implementation  
**Compatibility**: Claude Desktop 1.0+, CKAN 2.8+
