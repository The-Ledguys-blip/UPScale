# GitHub Actions - Automatic Windows MSI Build

Dit workflow bouwt automatisch `UPScale.msi` in de cloud.

## Setup (1 keer)

### 1. Zet project op GitHub

Als je project nog niet op GitHub staat:

```bash
cd /Users/kevinveen/Downloads/upscale-desktop-app

# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Add GitHub remote
git remote add origin https://github.com/YOUR-USERNAME/upscale-desktop-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2. Enable Actions

- Go to GitHub → Your repository
- Click **Settings** → **Actions** → **General**
- Make sure "Allow all actions and reusable workflows" is enabled

## Build MSI (Automatic)

De Windows installer wordt automatisch gebouwd wanneer je code pusht.

### Optie A: Auto-build op push

```bash
git push
# Workflow starts automatically
```

### Optie B: Manual trigger

- Go to GitHub → Your repository
- Click **Actions** → **Build Windows Installer**
- Click **Run workflow**

## Download MSI

### Method 1: From Artifacts (Builds)

1. Go to GitHub → Your repository
2. Click **Actions**
3. Click latest **Build Windows Installer**
4. Scroll down → **Artifacts**
5. Download **UPScale-Windows-Installer**
6. Extract → Get `UPScale.msi`

## Share

Share the downloaded MSI with users.

Users can run `UPScale.msi` with the normal Windows installer flow.

## Troubleshooting

### Build fails?
- Check GitHub Actions log for error
- Common issues:
  - Missing `app.ico` → Make sure it's in project root
  - Missing `led-pixelmap-tool_121.html` → Make sure path is correct
  - Fix and push again

### Slow build?
- First build takes 3-5 min (installs Python + deps)
- Subsequent builds are faster (~2 min)

## Notes

- ✅ Builds on cloud (no local build needed)
- ✅ Automatic on every push
- ✅ Artifacts available for 90 days
- ✅ Produces a real MSI installer

## Example Flow

```
1. You fix bug on Mac
2. git push origin main
3. GitHub Actions auto-builds on Windows
4. You download UPScale.msi from Actions
5. Share link to users
6. Users install and run
```

No manual Windows build machine needed.
