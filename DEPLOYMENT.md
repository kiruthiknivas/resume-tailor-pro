# Cloud Deployment & Mobile Guide — Resume Tailor Pro

This guide walks you through hosting **Resume Tailor Pro** online 24/7 in the cloud so you can use it from your **iPhone**, share it with **friends**, and generate ATS-compliant resumes anytime—**even when your laptop is completely powered off**.

---

## Why Not Netlify?
**Netlify** is designed specifically for static JAMstack websites (React, Vue, HTML/CSS) and lightweight serverless functions (with a 50MB package limit). Netlify **cannot run TeX Live or pdflatex**, which is required to compile your LaTeX resumes into pixel-perfect PDFs.

To compile LaTeX in the cloud, you need a **containerized cloud platform** that runs Docker with Python + TeX Live. The best **100% free** services for this are:
1. **Render.com** (Recommended: 1-click Docker Web Service with free SSL)
2. **Hugging Face Spaces** (Alternative: 100% free Docker space with 16GB RAM)

Both run 24/7 independently of your laptop.

---

## Option 1: Deploy to Render.com (Recommended)

### Step 1: Create a GitHub Repository
1. Open your browser and go to [github.com/new](https://github.com/new).
2. Repository name: `resume-tailor-pro`
3. Visibility: Choose **Public** or **Private** (both work).
4. Do **not** initialize with README or .gitignore (we already created them locally).
5. Click **Create repository**.

### Step 2: Push Your Local Code to GitHub
Open PowerShell or your terminal, navigate to your project directory, and run:

```bash
cd "C:\Users\nivas\.gemini\antigravity\scratch\resume-tailor"
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/resume-tailor-pro.git
git push -u origin main
```
*(Replace `<YOUR_GITHUB_USERNAME>` with your actual GitHub username).*

### Step 3: Launch on Render
1. Go to [render.com](https://render.com) and sign up / log in with your GitHub account.
2. Click the **"New +"** button at the top right and select **"Web Service"**.
3. Choose **"Build and deploy from a Git repository"** and click **Next**.
4. Select your `resume-tailor-pro` repository.
5. Render will automatically detect the `Dockerfile` and `render.yaml`.
   - **Name**: `resume-tailor-pro` (or any name you prefer)
   - **Region**: Choose closest to you (e.g., Singapore or Frankfurt or Oregon)
   - **Instance Type**: **Free**
6. Scroll down to **Environment Variables** and add:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: `<YOUR_GEMINI_API_KEY>`
   *(Optional secondary: `OPENAI_API_KEY` = `<YOUR_OPENAI_API_KEY>`)*
7. Click **"Deploy Web Service"**.

Render will now build the container (installing Python 3.12, TeX Live, and dependencies). Within 3-4 minutes, you will receive a permanent live URL:
```
https://resume-tailor-pro.onrender.com
```

---

## Option 2: Deploy to Hugging Face Spaces (Alternative)

Hugging Face Spaces provides 100% free Docker hosting with 16GB RAM.

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. Space name: `resume-tailor-pro`
3. License: `mit` or `apache-2.0`
4. Select **Docker** -> **Blank**.
5. Space hardware: **Free (2 vCPU, 16GB RAM)**.
6. Click **Create Space**.
7. Go to **Settings** -> **Variables and secrets** -> **New secret**:
   - Name: `GEMINI_API_KEY`
   - Value: `<YOUR_GEMINI_API_KEY>`
8. In your local terminal, add Hugging Face remote and push:
   ```bash
   git remote add hf https://huggingface.co/spaces/<YOUR_HF_USERNAME>/resume-tailor-pro
   git push hf main
   ```
Your space will build and launch automatically at `https://huggingface.co/spaces/<YOUR_HF_USERNAME>/resume-tailor-pro`!

---

## Using on iPhone (Mobile Web App)

Once your cloud URL is live:

### 1. Add as an App on your iPhone Home Screen
1. Open your live URL (e.g. `https://resume-tailor-pro.onrender.com`) in **Safari** on your iPhone.
2. Tap the **Share** button (box with an arrow pointing up) at the bottom toolbar.
3. Scroll down and tap **"Add to Home Screen"**.
4. Name it **"Resume Tailor"** and tap **Add**.
5. It now appears as a native app icon on your iPhone home screen!

### 2. The 60-Second Mobile Job Application Workflow
1. When browsing LinkedIn, Indeed, or career portals on your iPhone:
   - Copy the job description text.
2. Open **Resume Tailor** from your home screen.
3. Tap **"📋 Paste from Clipboard"** (instantly pastes the JD into the box).
4. Type the Company Name and select the Country.
5. Select your profile: **"Kiruthiknivas R"** (or switch to any friend's profile).
6. Tap **"✨ Generate Tailored Resume"**.
7. In ~5 seconds, your tailored PDF is ready!
8. Tap **"Download PDF"**:
   - Safari automatically saves it into your iPhone's **Files > iCloud Drive > Downloads** folder.
9. Switch back to your job application portal in Safari, tap **Upload Resume**, select **Files**, and pick your freshly generated PDF!

---

## Sharing with Friends

1. Send your live cloud link to your friends.
2. When they open the site, they click **"+ Add Friend's Resume"**.
3. They upload their existing resume (`.pdf`, `.docx`, or `.txt`).
4. The AI automatically parses their skills, experience, and projects into their own candidate profile.
5. Whenever they apply for jobs:
   - They select their name from the **Candidate Profile** dropdown.
   - Enter Company, Country, and JD.
   - Click Generate to get their own tailored, ATS-compliant 1-page resume!
   - Their PDF downloads directly to their device.

---

## Privacy & Security
- API keys are stored securely in cloud environment variables, not in public code.
- Resumes are generated in isolated temporary sandboxes and automatically served over encrypted HTTPS.
