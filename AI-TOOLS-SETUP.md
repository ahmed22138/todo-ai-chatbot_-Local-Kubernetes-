# 🤖 AI Tools Setup - Phase 4

## ✅ Installation Status

| Tool | Status | Installation | Functionality |
|------|--------|--------------|---------------|
| **Docker AI (Gordon)** | ✅ INSTALLED & WORKING | Pre-installed with Docker Desktop | Fully functional |
| **kubectl-ai** | ⚠️ INSTALLED (needs API key) | Downloaded & extracted | Requires OpenAI API key |
| **Kagent** | ❌ NOT AVAILABLE | Not found in standard repos | Alternative: k8sgpt |

---

## 1. ✅ Docker AI (Gordon) - WORKING

### Status: **Fully Functional** ✅

### Installation:
- **Pre-installed** with Docker Desktop 29.1.3
- No additional setup needed

### How to Use:

```bash
# Interactive mode
docker ai

# Single question
docker ai "How do I optimize my Docker images?"

# With command execution
docker ai "Show me all running containers" -s

# Help
docker ai --help
```

### Examples:

```bash
# Example 1: Ask about Docker commands
docker ai "How do I list all my Docker images?"

# Example 2: Get optimization tips
docker ai "How can I reduce the size of my todo-backend:1.0.0 image?"

# Example 3: Troubleshooting
docker ai "Why is my container not starting?"
```

### Features:
- ✅ Natural language Docker queries
- ✅ Command suggestions
- ✅ Documentation lookup
- ✅ Best practices recommendations
- ✅ Works offline (basic commands)
- ✅ Online mode for advanced queries

### Test Command:
```bash
docker ai "List all Docker images"
```

**Expected Output:**
```
To list all your Docker images, use:
docker images
or
docker image ls
```

---

## 2. ⚠️ kubectl-ai - INSTALLED (Needs Configuration)

### Status: **Installed but requires OpenAI API key** ⚠️

### Installation Location:
```
C:\Users\Hp\.kubectl-plugins\kubectl-ai.exe
```

### Configuration Required:

#### Step 1: Get OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Create new API key
3. Copy the key (starts with `sk-`)

#### Step 2: Set Environment Variable

**Windows PowerShell:**
```powershell
# Temporary (current session only)
$env:OPENAI_API_KEY="sk-your-api-key-here"

# Permanent (all sessions)
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-api-key-here', 'User')
```

**Windows CMD:**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Git Bash:**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### How to Use:

```bash
# Add to PATH first (Git Bash)
export PATH="$HOME/.kubectl-plugins:$PATH"

# Or use full path
~/.kubectl-plugins/kubectl-ai.exe --help

# Examples (after API key is set):
kubectl-ai "create a nginx deployment"
kubectl-ai "scale my deployment to 3 replicas"
kubectl-ai "show me all failing pods"
```

### Features:
- ✅ Natural language kubectl commands
- ✅ Resource generation from descriptions
- ✅ Troubleshooting help
- ⚠️ Requires OpenAI API key (paid service)

### Test Command (after setting API key):
```bash
kubectl-ai "list all pods in default namespace"
```

---

## 3. ❌ Kagent - NOT AVAILABLE

### Status: **Not found in standard repositories** ❌

### Investigation Results:
- No official `kagent` tool found in major Kubernetes repositories
- Possible confusion with `k8sgpt` or `kagenti`
- May be a proprietary or discontinued tool

### Alternative Recommended: **k8sgpt**

**k8sgpt** is a similar Kubernetes AI diagnostics tool:

#### Installation (Windows):

**Via Chocolatey:**
```powershell
choco install k8sgpt
```

**Via Winget:**
```powershell
winget install k8sgpt
```

**Manual Download:**
```bash
# Download from GitHub releases
# https://github.com/k8sgpt-ai/k8sgpt/releases
```

#### k8sgpt Features:
- AI-powered Kubernetes diagnostics
- Problem detection and solutions
- Integration with OpenAI, Azure OpenAI, or local models
- Scans clusters for issues
- Provides remediation steps

#### k8sgpt Usage:
```bash
# Analyze cluster
k8sgpt analyze

# Explain issues
k8sgpt analyze --explain

# Filter by namespace
k8sgpt analyze -n default

# Generate fixes
k8sgpt analyze --fix
```

---

## 🎯 Current Working Setup

### ✅ What's Working NOW:

#### 1. Docker AI (Gordon) - 100% Ready
```bash
# Test it right now:
docker ai "What are best practices for Docker images?"
```

#### 2. kubectl-ai - 90% Ready
- ✅ Binary installed
- ⚠️ Needs OpenAI API key to function
- Set `OPENAI_API_KEY` environment variable

---

## 📋 Quick Setup Guide

### For Docker AI (Gordon):
```bash
# Already working - just use it!
docker ai "your question here"
```

### For kubectl-ai:
```bash
# Step 1: Set API key (get from OpenAI)
export OPENAI_API_KEY="sk-your-key-here"

# Step 2: Add to PATH
export PATH="$HOME/.kubectl-plugins:$PATH"

# Step 3: Test
kubectl-ai "list pods"
```

### For Kagent Alternative (k8sgpt):
```powershell
# Install via package manager
choco install k8sgpt
# OR
winget install k8sgpt

# Configure
k8sgpt auth add --backend openai --key sk-your-key-here

# Use
k8sgpt analyze
```

---

## 🔑 OpenAI API Key Setup

If you want to use kubectl-ai or k8sgpt with OpenAI:

### Get API Key:
1. Visit: https://platform.openai.com/api-keys
2. Sign up/Login
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. ⚠️ Store it securely - you can't see it again!

### Set in Windows:

**PowerShell (Permanent):**
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key', 'User')
```

**Git Bash:**
```bash
echo 'export OPENAI_API_KEY="sk-your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Verify:
```bash
echo $OPENAI_API_KEY
# Should show your key
```

---

## 🎉 Summary

| Tool | Status | Usable Now? | Requires |
|------|--------|-------------|----------|
| **Docker AI (Gordon)** | ✅ Working | YES | Nothing - just use it! |
| **kubectl-ai** | ⚠️ Installed | YES (with API key) | OpenAI API key |
| **Kagent** | ❌ Not found | NO | Alternative: k8sgpt |

---

## 🚀 Recommended Next Steps

### Immediate (No cost):
1. ✅ **Use Docker AI (Gordon)** - Already working!
   ```bash
   docker ai "optimize my todo-backend image"
   ```

### Optional (Requires OpenAI account):
2. **Get OpenAI API key** (free tier available)
3. **Enable kubectl-ai** with your API key
4. **Test kubectl-ai** with simple commands

### Advanced (Optional):
5. **Install k8sgpt** for cluster diagnostics
6. **Configure k8sgpt** with OpenAI or local LLM
7. **Run cluster analysis**

---

## 📝 Testing Commands

### Test Docker AI (Gordon):
```bash
docker ai "List all containers"
docker ai "Show me disk usage"
docker ai "How to clean unused images?"
```

### Test kubectl-ai (after API key setup):
```bash
kubectl-ai "get all pods"
kubectl-ai "create nginx deployment with 3 replicas"
kubectl-ai "troubleshoot pod errors"
```

---

## 🔧 Troubleshooting

### Docker AI not responding:
```bash
# Check Docker is running
docker ps

# Restart Docker Desktop
```

### kubectl-ai "Please provide OpenAI key":
```bash
# Set the environment variable
export OPENAI_API_KEY="sk-your-key-here"

# Verify it's set
echo $OPENAI_API_KEY
```

### Can't find kubectl-ai:
```bash
# Add to PATH
export PATH="$HOME/.kubectl-plugins:$PATH"

# Or use full path
~/.kubectl-plugins/kubectl-ai.exe --help
```

---

**Last Updated:** 2026-01-08
**Status:**
- ✅ Docker AI (Gordon): WORKING
- ⚠️ kubectl-ai: INSTALLED (needs API key)
- ❌ Kagent: NOT AVAILABLE (use k8sgpt instead)
