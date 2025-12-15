# AgriGPT Backend RAG - Installation Guide

> **🔗 Related Repository**: For the frontend setup, see [AgriGPT Frontend](https://github.com/alumnx-ai-labs/agrigpt-frontend)

This comprehensive guide will walk you through setting up the AgriGPT Backend RAG on your local machine. Whether you're using Linux, Windows, or macOS, this guide has you covered - even if you're completely new to Git, GitHub, or Python!

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Git and GitHub Basics](#-git-and-github-basics)
3. [Installing Python 3.11](#-installing-python-311)
4. [Getting the Code](#-getting-the-code)
5. [Setting Up Virtual Environment](#-setting-up-virtual-environment)
6. [Getting API Keys](#-getting-api-keys)
7. [Environment Configuration](#-environment-configuration)
8. [Installing Dependencies](#-installing-dependencies)
9. [Setting Up Pinecone Index](#-setting-up-pinecone-index)
10. [Running the Application](#-running-the-application)
11. [Troubleshooting](#-troubleshooting)
12. [Next Steps](#-next-steps)

---

## ✅ Prerequisites

Before you begin, you'll need:

- A computer running **Linux**, **Windows**, or **macOS**
- An internet connection
- Basic familiarity with using the command line/terminal
- A text editor (we recommend [VS Code](https://code.visualstudio.com/))
- Willingness to create free accounts for API services

---

## 🔰 Git and GitHub Basics

### What is Git?

Git is a version control system that helps track changes in your code. GitHub is a platform that hosts Git repositories online.

### Installing Git

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install git

# Fedora
sudo dnf install git

# Arch Linux
sudo pacman -S git
```

#### Windows

1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Run the installer
3. Use default settings (recommended for beginners)
4. Open "Git Bash" from the Start menu to use Git

#### macOS

```bash
# Using Homebrew (recommended)
brew install git

# Or download from https://git-scm.com/download/mac
```

### Verify Git Installation

Open your terminal/command prompt and run:

```bash
git --version
```

You should see output like `git version 2.x.x`

### Configure Git (First Time Only)

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"
```

### Understanding GitHub

- **Repository (Repo)**: A project folder containing all files and their history
- **Clone**: Download a copy of a repository to your computer
- **Fork**: Create your own copy of someone else's repository on GitHub
- **Commit**: Save changes to your local repository
- **Push**: Upload your local changes to GitHub
- **Pull**: Download changes from GitHub to your local repository

---

## 🐍 Installing Python 3.11

> **⚠️ Important**: This project requires **Python 3.11.x** specifically. Python 3.12 or 3.13 may not work due to package compatibility issues.

### Linux

#### Ubuntu/Debian

```bash
# Add deadsnakes PPA for Python 3.11
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

#### Fedora

```bash
# Python 3.11 should be available in Fedora 36+
sudo dnf install python3.11 python3.11-devel

# Verify installation
python3.11 --version
```

#### Arch Linux

```bash
# Install from official repositories
sudo pacman -S python

# Or install specific version from AUR
yay -S python311

# Verify installation
python3.11 --version
```

### Windows

#### Option 1: Using Official Installer (Recommended)

1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download **Python 3.11.x** (latest 3.11 version)
3. Run the installer
4. **IMPORTANT**: Check "Add Python 3.11 to PATH" during installation
5. Click "Install Now"
6. Restart your computer after installation

#### Option 2: Using Microsoft Store

1. Open Microsoft Store
2. Search for "Python 3.11"
3. Click "Get" to install

#### Verify Installation (Windows)

Open Command Prompt or PowerShell:

```cmd
python --version
# or
python3 --version
# or
py -3.11 --version
```

### macOS

#### Option 1: Using Homebrew (Recommended)

```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Add to PATH
echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify installation
python3.11 --version
```

#### Option 2: Using Official Installer

1. Visit [python.org/downloads/macos](https://www.python.org/downloads/macos/)
2. Download **Python 3.11.x** installer
3. Run the `.pkg` file
4. Follow the installation wizard

### Verify pip Installation

pip is Python's package installer and should come with Python:

```bash
# Linux/macOS
python3.11 -m pip --version

# Windows
python -m pip --version
# or
py -3.11 -m pip --version
```

### Troubleshooting Python Installation

**Issue**: `python: command not found`

**Solution**:

- Restart your terminal/command prompt
- On Windows, restart your computer
- Verify Python is in your PATH environment variable
- Try `python3` or `python3.11` instead of `python`

**Issue**: Wrong Python version

**Solution**: Use the full command `python3.11` instead of `python` or `python3`

---

## 💻 Getting the Code

### Option 1: Clone the Repository (Recommended)

This is the simplest way to get started:

```bash
# Navigate to where you want to store the project
cd ~/Documents  # Linux/macOS
cd C:\Users\YourName\Documents  # Windows

# Clone the repository
git clone https://github.com/alumnx-ai-labs/agrigpt-backend-rag.git

# Navigate into the project folder
cd agrigpt-backend-rag
```

### Option 2: Fork and Clone (For Contributors)

If you plan to contribute to the project:

1. **Fork the Repository**:

   - Go to [github.com/alumnx-ai-labs/agrigpt-backend-rag](https://github.com/alumnx-ai-labs/agrigpt-backend-rag)
   - Click the "Fork" button in the top-right corner
   - This creates a copy under your GitHub account

2. **Clone Your Fork**:

   ```bash
   # Replace YOUR_USERNAME with your GitHub username
   git clone https://github.com/YOUR_USERNAME/agrigpt-backend-rag.git
   cd agrigpt-backend-rag
   ```

3. **Add Upstream Remote**:

   ```bash
   # This allows you to sync with the original repository
   git remote add upstream https://github.com/alumnx-ai-labs/agrigpt-backend-rag.git

   # Verify remotes
   git remote -v
   ```

### Option 3: Download ZIP

If you don't want to use Git:

1. Go to [github.com/alumnx-ai-labs/agrigpt-backend-rag](https://github.com/alumnx-ai-labs/agrigpt-backend-rag)
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to your desired location
5. Open terminal/command prompt in that folder

---

## 🔧 Setting Up Virtual Environment

A virtual environment keeps your project dependencies isolated from other Python projects.

### Why Use a Virtual Environment?

- Prevents conflicts between different projects
- Keeps your global Python installation clean
- Makes it easy to reproduce the exact environment
- Required for this project!

### Creating Virtual Environment

#### Linux/macOS

```bash
# Navigate to project directory
cd agrigpt-backend-rag

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

#### Windows (Command Prompt)

```cmd
# Navigate to project directory
cd agrigpt-backend-rag

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Your prompt should now show (venv)
```

#### Windows (PowerShell)

```powershell
# Navigate to project directory
cd agrigpt-backend-rag

# Create virtual environment
python -m venv venv

# You may need to enable script execution first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate virtual environment
venv\Scripts\Activate.ps1

# Your prompt should now show (venv)
```

### Deactivating Virtual Environment

When you're done working:

```bash
deactivate
```

### Always Activate Before Working

**Remember**: Every time you open a new terminal to work on this project, you must activate the virtual environment first!

```bash
# Linux/macOS
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

---

## 🔑 Getting API Keys

This project requires several API keys. Don't worry - most have free tiers!

### 1. Google AI API Key (Required)

**What it's for**: Powers the AI language model (Gemini)

**How to get it**:

1. Visit [ai.google.dev](https://ai.google.dev/)
2. Click "Get API key in Google AI Studio"
3. Sign in with your Google account
4. Click "Create API Key"
5. Copy the key (starts with `AIza...`)

**Free Tier**: Yes! Generous free quota for development

### 2. Pinecone API Key (Required)

**What it's for**: Vector database for storing document embeddings

**How to get it**:

1. Visit [pinecone.io](https://www.pinecone.io/)
2. Click "Sign Up" (free account)
3. Verify your email
4. Go to [app.pinecone.io](https://app.pinecone.io/)
5. Navigate to "API Keys" in the left sidebar
6. Copy your API key
7. Note your environment (e.g., `us-east-1`)

**Free Tier**: Yes! 1 index, 100K vectors

### 3. LangSmith API Key (Optional)

**What it's for**: Observability and debugging for LangChain applications

**How to get it**:

1. Visit [smith.langchain.com](https://smith.langchain.com/)
2. Sign up for a free account
3. Go to Settings → API Keys
4. Create a new API key
5. Copy the key

**Free Tier**: Yes! Limited to 5K traces/month

**Note**: This is optional - the app works without it, but you won't have observability features.

### 4. Cloudflare R2 (Optional)

**What it's for**: Cloud storage for uploaded files

**How to get it**:

1. Visit [cloudflare.com](https://www.cloudflare.com/)
2. Sign up for Cloudflare account
3. Go to R2 Object Storage
4. Create a bucket
5. Generate API tokens

**Free Tier**: Yes! 10GB storage

**Note**: This is optional - the app can use local storage instead.

### Keeping Your API Keys Safe

> **⚠️ CRITICAL SECURITY REMINDER**:
>
> - Never share your API keys publicly
> - Never commit them to Git
> - Never post them in issues or forums
> - Treat them like passwords!

---

## 🔐 Environment Configuration

Now we'll set up your environment variables with the API keys.

### Step 1: Create Environment File

#### Linux/macOS

```bash
# Make sure you're in the project directory
cd agrigpt-backend-rag

# Copy the template
cp .env.template .env
```

#### Windows (Command Prompt)

```cmd
copy .env.template .env
```

#### Windows (PowerShell)

```powershell
Copy-Item .env.template .env
```

### Step 2: Edit Environment Variables

Open the `.env` file in your text editor:

```bash
# Linux/macOS
nano .env
# or
code .env  # If you have VS Code

# Windows
notepad .env
# or
code .env  # If you have VS Code
```

### Step 3: Fill in Your API Keys

Replace the placeholder values with your actual API keys:

```env
# Google AI (Required)
GOOGLE_API_KEY=your_actual_google_api_key_here

# Pinecone (Required)
PINECONE_API_KEY=your_actual_pinecone_api_key_here
PINECONE_INDEX_NAME=agrigpt-backend-rag-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# LangSmith (Optional - for observability)
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=agrigpt-backend-rag

# Cloudflare R2 (Optional - for cloud storage)
# R2_ACCOUNT_ID=your_r2_account_id
# R2_ACCESS_KEY_ID=your_r2_access_key
# R2_SECRET_ACCESS_KEY=your_r2_secret_key
# R2_BUCKET_NAME=your_bucket_name
# R2_PUBLIC_URL=your_public_url
```

### Environment Variables Explained

| Variable              | Required | Description                 | Example                     |
| --------------------- | -------- | --------------------------- | --------------------------- |
| `GOOGLE_API_KEY`      | Yes      | Google AI API key           | `AIzaSy...`                 |
| `PINECONE_API_KEY`    | Yes      | Pinecone API key            | `abc123...`                 |
| `PINECONE_INDEX_NAME` | Yes      | Name of your Pinecone index | `agrigpt-backend-rag-index` |
| `PINECONE_CLOUD`      | Yes      | Cloud provider              | `aws` or `gcp`              |
| `PINECONE_REGION`     | Yes      | Region for Pinecone         | `us-east-1`                 |
| `LANGSMITH_API_KEY`   | No       | LangSmith API key           | `ls__...`                   |
| `LANGSMITH_TRACING`   | No       | Enable tracing              | `true` or `false`           |
| `LANGSMITH_PROJECT`   | No       | Project name                | `agrigpt-backend-rag`       |

> **💡 Tip**: Leave the optional R2 variables commented out (with `#`) if you're not using cloud storage.

---

## 📥 Installing Dependencies

Now we'll install all the required Python packages.

### Make Sure Virtual Environment is Activated

You should see `(venv)` in your terminal prompt. If not:

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Install All Dependencies

```bash
pip install -r requirements.txt
```

This command will:

- Read `requirements.txt` to see what packages are needed
- Download all packages from PyPI (Python Package Index)
- Install them in your virtual environment

### What Gets Installed?

The main dependencies include:

- **FastAPI** - Web framework
- **LangChain 0.2.x** - LLM application framework
- **Pinecone** - Vector database client
- **Google Generative AI** - Gemini API client
- **CLIP** - Multimodal embeddings
- **PyPDF2** - PDF processing
- **Uvicorn** - ASGI server

### Installation Time

- First install: 3-7 minutes (depending on internet speed)
- Downloads approximately 500MB of packages

### Verify Installation

```bash
# Check if FastAPI is installed
python -c "import fastapi; print(fastapi.__version__)"

# Check if LangChain is installed
python -c "import langchain; print(langchain.__version__)"
```

### Troubleshooting Installation

**Issue**: `pip: command not found`

**Solution**:

```bash
# Use python -m pip instead
python -m pip install -r requirements.txt
```

**Issue**: `error: Microsoft Visual C++ 14.0 is required` (Windows)

**Solution**: Install Visual C++ Build Tools:

1. Download from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Run installer
3. Select "Desktop development with C++"
4. Install and restart

**Issue**: `Permission denied` (Linux/macOS)

**Solution**: Make sure virtual environment is activated. Never use `sudo pip`!

**Issue**: Package conflicts or version errors

**Solution**:

```bash
# Upgrade pip first
pip install --upgrade pip

# Then try again
pip install -r requirements.txt
```

---

## 🗄️ Setting Up Pinecone Index

Before running the application, you need to create a Pinecone index.

### Step 1: Log in to Pinecone

1. Go to [app.pinecone.io](https://app.pinecone.io/)
2. Sign in with your account

### Step 2: Create an Index

1. Click "Create Index" or "Indexes" in the left sidebar
2. Click the "+ Create Index" button
3. Fill in the details:

   **Index Configuration**:

   - **Name**: `agrigpt-backend-rag-index` (must match your `.env`)
   - **Dimensions**: `768`
   - **Metric**: `cosine`
   - **Cloud Provider**: `AWS` (or your preferred provider)
   - **Region**: `us-east-1` (or your preferred region)

4. Click "Create Index"
5. Wait for the index to be ready (usually 1-2 minutes)

### Step 3: Verify Index Settings

Make sure your `.env` file matches:

```env
PINECONE_INDEX_NAME=agrigpt-backend-rag-index  # Must match index name
PINECONE_CLOUD=aws                              # Must match cloud provider
PINECONE_REGION=us-east-1                       # Must match region
```

### Why These Settings?

- **Dimensions: 768**: Required for CLIP embeddings
- **Metric: cosine**: Best for semantic similarity search
- **Cloud/Region**: Choose closest to you for better performance

### Troubleshooting Pinecone

**Issue**: "Index not found" error

**Solution**:

- Verify index name in `.env` matches exactly
- Check index is in "Ready" state in Pinecone console
- Wait a few minutes after creation

**Issue**: "Invalid dimensions" error

**Solution**: Delete and recreate index with dimensions = 768

---

## 🚀 Running the Application

### Start the Development Server

Make sure:

1. Virtual environment is activated (`(venv)` in prompt)
2. You're in the project directory
3. `.env` file is configured
4. Pinecone index is created

Then run:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Access the Application

1. **API**: http://localhost:8000
2. **Interactive Docs**: http://localhost:8000/docs
3. **Health Check**: http://localhost:8000/health

### Test the Health Endpoint

Open a new terminal and run:

```bash
curl http://localhost:8000/health
```

You should see:

```json
{
  "status": "healthy",
  "service": "RAG Chatbot API",
  "services_ready": true,
  "clip_available": true,
  "clip_import_error": null
}
```

### Development Server Features

- **Auto-reload**: Changes to code automatically restart the server
- **Interactive Docs**: Test API endpoints at `/docs`
- **Fast Performance**: ASGI server for high concurrency

### Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

### Other Useful Commands

```bash
# Run without auto-reload (production-like)
uvicorn main:app --host 0.0.0.0 --port 8000

# Run on different port
uvicorn main:app --reload --port 8080

# Run with more workers (production)
uvicorn main:app --workers 4
```

---

## 🔍 Troubleshooting

### Port Already in Use

**Error**: `Address already in use`

**Solution**:

```bash
# Option 1: Kill the process using the port
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows (PowerShell as Admin)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Option 2: Use a different port
uvicorn main:app --reload --port 8080
```

### API Key Errors

**Error**: `Invalid API key` or `Authentication failed`

**Solution**:

1. Verify API keys in `.env` are correct
2. Check for extra spaces or quotes
3. Regenerate API keys if needed
4. Restart the server after changing `.env`

### Pinecone Connection Errors

**Error**: `Failed to connect to Pinecone`

**Solution**:

1. Check internet connection
2. Verify Pinecone API key is correct
3. Ensure index exists and is in "Ready" state
4. Check region and cloud settings match

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'xyz'`

**Solution**:

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Python Version Issues

**Error**: `SyntaxError` or compatibility errors

**Solution**:

```bash
# Verify Python version
python --version

# Should be 3.11.x
# If not, use python3.11 explicitly:
python3.11 -m venv venv
```

### CLIP/Torch Installation Issues

**Error**: Errors related to `torch` or `clip`

**Solution**:

```bash
# Install PyTorch separately first
pip install torch torchvision

# Then install other dependencies
pip install -r requirements.txt
```

### Platform-Specific Issues

#### Linux

- **Issue**: `libgomp` or `libstdc++` errors
- **Solution**:
  ```bash
  sudo apt install libgomp1 libstdc++6
  ```

#### Windows

- **Issue**: Long path errors
- **Solution**: Enable long paths in Windows settings or use shorter project path

#### macOS

- **Issue**: SSL certificate errors
- **Solution**:
  ```bash
  /Applications/Python\ 3.11/Install\ Certificates.command
  ```

---

## 🎯 Next Steps

Congratulations! You've successfully set up the AgriGPT Backend RAG. Here's what to do next:

### 1. Set Up the Frontend

The backend provides the API, but you'll need the frontend for the user interface:

- [AgriGPT Frontend Installation Guide](https://github.com/alumnx-ai-labs/agrigpt-frontend/blob/main/docs/INSTALLATION.md)

### 2. Test the API

Visit http://localhost:8000/docs to:

- Upload a PDF document
- Send chat queries
- Test all endpoints interactively

### 3. Explore the Code

- **`main.py`** - FastAPI application entry point
- **`routes/`** - API endpoint definitions
- **`services/`** - Business logic and integrations
- **`requirements.txt`** - Python dependencies

### 4. Read the Documentation

- [README.md](../README.md) - Project overview and features
- [CONTRIBUTING.md](./CONTRIBUTING.md) - How to contribute
- [USAGE_GUIDE.md](../USAGE_GUIDE.md) - How to use the API

### 5. Start Contributing

If you want to contribute:

1. Read the [Contributing Guide](./CONTRIBUTING.md)
2. Look for issues labeled `good first issue`
3. Fork the repository and create a branch
4. Make your changes and submit a pull request

### 6. Join the Community

- Report bugs or request features via [GitHub Issues](https://github.com/alumnx-ai-labs/agrigpt-backend-rag/issues)
- Star the repository if you find it useful!

---

## 📚 Additional Resources

### Learning Resources

- **FastAPI**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **LangChain**: [python.langchain.com](https://python.langchain.com/)
- **Pinecone**: [docs.pinecone.io](https://docs.pinecone.io/)
- **Python**: [docs.python.org](https://docs.python.org/3/)
- **Git**: [git-scm.com/doc](https://git-scm.com/doc)

### Command Reference

```bash
# Virtual Environment
python3.11 -m venv venv          # Create virtual environment
source venv/bin/activate         # Activate (Linux/macOS)
venv\Scripts\activate            # Activate (Windows)
deactivate                       # Deactivate

# Package Management
pip install -r requirements.txt  # Install dependencies
pip list                         # List installed packages
pip freeze                       # Show installed versions

# Running the Server
uvicorn main:app --reload        # Development mode
uvicorn main:app                 # Production mode
uvicorn main:app --port 8080     # Custom port

# Git Commands
git clone <url>                  # Clone repository
git pull                         # Update local repository
git status                       # Check status
git add .                        # Stage changes
git commit -m "message"          # Commit changes
git push                         # Push to remote
```

---

## 🆘 Getting Help

If you're stuck:

1. **Check this guide** - Search for your issue in the Troubleshooting section
2. **Check the logs** - Error messages often explain the problem
3. **Search existing issues** - Someone might have had the same problem
4. **Ask for help** - Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Error messages (full text)
   - Steps you've already tried
   - Contents of your `.env` (without actual API keys!)

---

**Made with ❤️ by the AgriGPT Team**

[⬆ Back to Top](#agrigpt-backend-rag---installation-guide)
