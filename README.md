# Resume Tailor Pro (Multi-Profile & Mobile Edition)

> **AI-Powered, ATS-Optimized Resume Generator & Multi-Candidate Platform**  
> Custom tailored for **Kiruthiknivas R** with iCloud sync + full multi-candidate friend profile management.

---

## What's New in v3.0

1. **Multi-Profile Support for Friends**:
   - Add as many candidate profiles as you want.
   - Upload any friend's existing resume in **PDF**, **Word DOCX**, or **Text** format.
   - The AI parser automatically extracts their name, contact details, summary, technical skills, employment history, and education into an ATS profile.
   - Switch between candidates with a single dropdown click.

2. **iPhone & Mobile Support**:
   - Responsive web interface designed for iOS Safari and mobile browsers (touch-friendly targets, no zoom quirks).
   - Quick **"Paste from Clipboard"** button for easy 1-tap pasting of Job Descriptions from LinkedIn/Indeed apps.
   - **Direct iPhone/LAN Access**: Accessible on your local Wi-Fi at:  
     👉 `http://192.168.0.141:5000`
   - **iCloud Drive Auto-Sync**: Resumes generated for Kiruthiknivas automatically save to `C:\Users\nivas\iCloudDrive\Resume\One page Resume\` and sync straight into your **iPhone Files app** within seconds!
   - **Direct PDF Download & Preview**: Friends get a direct download button and in-browser preview without touching your iCloud.

3. **Pixel-Perfect Alignment & Guaranteed 1-Page Output**:
   - Fixed all negative vertical skips to prevent text collisions.
   - Typographic spacing calibrated for exactly 1 page.
   - Human-authentic tone with zero AI detection flags.

---

## Quick Start

### 1. Run on PC
Double-click:
```
C:\Users\nivas\.gemini\antigravity\scratch\resume-tailor\start.bat
```
Or via PowerShell:
```powershell
cd C:\Users\nivas\.gemini\antigravity\scratch\resume-tailor
.\run.ps1
```

### 2. Access Links
- **From your PC**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **From your iPhone**: Connect to the same Wi-Fi, open Safari, and go to:  
  **`http://192.168.0.141:5000`**

---

## How to Tailor a Resume for a Friend

1. Open the site and click **"+ Add / Upload Friend's Resume"** in the candidate box.
2. Drag & drop or browse their resume (`.pdf`, `.docx`, or `.txt`).
3. Click **"Analyze & Save Profile"**.
4. The AI parses their document and selects their profile in the dropdown.
5. Enter the target **Company Name**, **Country**, and paste the **Job Description**.
6. Click **"Generate ATS-Optimized Resume"**.
7. Tap **"Download Resume"** or **"View PDF"** to give them their tailored 1-page PDF!

---

## Backup Location

Before adding multi-profile and mobile features, a complete standalone backup of your initial working version was created at:
```
C:\Users\nivas\.gemini\antigravity\scratch\resume-tailor-backup-v1\
```

---

## Free Public Online Sharing Options

If you want your friends outside your home Wi-Fi to access the app:

### Option 1: Cloudflare Tunnel (Free & Instant, No Port Forwarding)
```powershell
# In PowerShell:
winget install Cloudflare.cloudflared
cloudflared tunnel --url http://127.0.0.1:5000
```
Cloudflare will give you a public HTTPS URL (e.g. `https://random-words.trycloudflare.com`) that you can share with anyone anywhere.

### Option 2: LocalTunnel (No Installation)
```powershell
npx localtunnel --port 5000
```
