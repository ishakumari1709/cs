# 🚀 Render Deployment Guide - Fixed All Errors

## ⚠️ Important: Manual Configuration Required

Render is **NOT automatically using** `render.yaml` when you connect via GitHub. You need to **manually configure** the build settings.

## 🔧 Step-by-Step Fix

### Step 1: Go to Render Dashboard

1. Go to https://render.com
2. Click on your **Web Service** (customer-support-backend)

### Step 2: Update Python Version

1. Go to **Settings** → **Environment**
2. Find **Python Version** (or create it)
3. Set to: `3.11`
4. **Save Changes**

### Step 3: Update Build Command

1. Go to **Settings** → **Build & Deploy**
2. Find **Build Command**
3. **Replace** with this exact command:

```bash
export CARGO_HOME=/tmp/cargo && export RUSTUP_HOME=/tmp/rustup && export PIP_NO_BUILD_ISOLATION=1 && pip install --upgrade pip setuptools wheel && pip install numpy && pip install --prefer-binary --no-cache-dir -r requirements.txt
```

4. **Save Changes**

### Step 4: Verify Start Command

1. In **Settings** → **Build & Deploy**
2. Verify **Start Command** is:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 5: Add Environment Variables

Go to **Environment** tab and add:

- `HUGGINGFACE_API_KEY` = your key
- `FRONTEND_URL` = (leave empty for now, add after frontend deployment)

### Step 6: Manual Deploy

1. Go to **Manual Deploy** tab
2. Click **Deploy latest commit**
3. Wait 5-10 minutes

## 🔄 Alternative: Use requirements-render.txt

If still having issues, update Build Command to use the optimized requirements:

```bash
export CARGO_HOME=/tmp/cargo && export RUSTUP_HOME=/tmp/rustup && export PIP_NO_BUILD_ISOLATION=1 && pip install --upgrade pip setuptools wheel && pip install numpy && pip install --prefer-binary --no-cache-dir -r requirements-render.txt
```

## ✅ What Was Fixed

1. **Python Version**: Set to 3.11 (3.13 has compatibility issues)
2. **Build Command**: Added Rust/Cargo environment variables
3. **PIP_NO_BUILD_ISOLATION**: Prevents isolated builds that cause issues
4. **--prefer-binary**: Uses pre-built wheels instead of compiling
5. **Updated pydantic**: Pinned to version with pre-built wheels

## 🐛 Common Issues

### Issue: "Python 3.13" in logs
**Fix**: Manually set Python version to 3.11 in Render settings

### Issue: Still getting Rust errors
**Fix**: Make sure Build Command includes all environment variables:
```bash
export CARGO_HOME=/tmp/cargo && export RUSTUP_HOME=/tmp/rustup && export PIP_NO_BUILD_ISOLATION=1
```

### Issue: Build timeout
**Fix**: Use `requirements-render.txt` (removes OCR dependencies)

## 📋 Checklist

- [ ] Python version set to 3.11 in Render
- [ ] Build Command updated with Rust environment variables
- [ ] Start Command is correct
- [ ] Environment variables added
- [ ] Manual deploy triggered
- [ ] Build completes successfully
- [ ] `/docs` endpoint works

## 🎉 Success Indicators

You'll know it worked when:
- ✅ Build logs show "Successfully installed..."
- ✅ No Rust/Cargo errors
- ✅ Service status is "Live"
- ✅ `https://your-backend.onrender.com/docs` works

