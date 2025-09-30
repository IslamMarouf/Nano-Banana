# 🔍 Troubleshooting Guide

## Current Issues:

### 1. Gallery Shows "No images yet" ❌
### 2. Batch Mode Shows "HTTP 404" ❌

---

## 🔧 **Debugging Steps:**

### **Step 1: Open Browser Console**

1. Open http://127.0.0.1:10000/web
2. Press `F12` to open Developer Tools
3. Go to "Console" tab
4. Keep it open while testing

### **Step 2: Test Create Mode**

1. Go to Create tab
2. Type a prompt: "a beautiful sunset"
3. Click "Generate Image"
4. **Watch the console** - you should see:
   ```
   Create response: {created: ..., data: [...]}
   Adding to gallery: {id: ..., type: "create", ...}
   Gallery add result: true
   Loading gallery...
   Gallery items: 1
   ```

5. **If you see errors**, copy them and tell me!

### **Step 3: Test Gallery Endpoint**

Open this in a new tab:
```
http://127.0.0.1:10000/v1/gallery
```

You should see:
```json
{"items": [], "total": 0}
```

If you see 404, the endpoint doesn't exist!

### **Step 4: Test Batch Endpoint**

1. Open test file: `file:///d:/PROGRAMS/Nano-Banana/test_endpoints.html`
2. Click "Test Batch"
3. Should show status 422 (missing files) NOT 404
4. If 404, endpoint doesn't exist!

---

## 🐛 **Possible Issues:**

### **Issue A: Server Running Old Code**

**Symptoms:**
- Batch shows 404
- Gallery endpoint doesn't exist

**Solution:**
```bash
# Make SURE server is stopped
# Press Ctrl+C multiple times

# Check no python process running
Get-Process python

# If any running, kill them
Stop-Process -Name python -Force

# Start fresh
python main.py
```

### **Issue B: Wrong Port**

**Check:**
```bash
netstat -ano | findstr :10000
```

Should show:
```
TCP    127.0.0.1:10000    ...    LISTENING
```

### **Issue C: CORS Issues**

**Check browser console** for:
```
Access-Control-Allow-Origin
```

If you see this, the server needs CORS enabled (it should be already).

### **Issue D: Gallery Not Persisting**

**This is NORMAL!**

Gallery data is stored in memory. When you restart the server, it's empty!

**To test:**
1. Generate an image
2. DON'T restart server
3. Check gallery - should show image
4. Restart server
5. Check gallery - will be empty (expected!)

---

## 📊 **Expected Behavior:**

### **Create/Edit Image:**
1. Click Generate/Edit
2. Wait for processing (10-30 seconds)
3. See success toast
4. Switch to Gallery tab
5. **Image should appear!**

### **Batch Processing:**
1. Upload 2-3 images
2. Enter prompt
3. Click "Process All Images"
4. Should NOT show 404
5. Should show progress bars
6. Switch to gallery
7. All images appear

---

## 🔍 **What to Check:**

### **In Browser Console:**

**Good Signs:**
```
Create response: {...}
Adding to gallery: {...}
Gallery add result: true
Gallery items: 1
```

**Bad Signs:**
```
Failed to fetch
404 Not Found
CORS error
```

### **In Server Terminal:**

**Good Signs:**
```
INFO - Received image generation request
INFO - Image generation succeeded
INFO - Upload successful
```

**Bad Signs:**
```
ERROR - ...
404 - Not Found
500 - Internal Server Error
```

---

## 🚨 **If Still Not Working:**

### **Do This:**

1. **Stop ALL Python processes:**
```bash
Stop-Process -Name python -Force
```

2. **Check main.py has these lines:**
```bash
Get-Content main.py | Select-String -Pattern "@app.get\(`"/v1/gallery"
Get-Content main.py | Select-String -Pattern "@app.post\(`"/v1/batch"
```

Should show both endpoints exist!

3. **Start server with verbose logging:**
```bash
python main.py
```

4. **Test endpoints directly:**

Open browser and go to:
- http://127.0.0.1:10000/health (should work)
- http://127.0.0.1:10000/v1/gallery (should return JSON)
- http://127.0.0.1:10000/docs (should show API docs)

5. **Check API docs:**

Go to: http://127.0.0.1:10000/docs

Look for:
- `/v1/gallery` GET endpoint
- `/v1/gallery` POST endpoint  
- `/v1/batch` POST endpoint

If ANY are missing, server is running old code!

---

## 📝 **Report Back:**

Please tell me:

1. **What you see in browser console** when you click Generate
2. **What you see in server terminal** when you click Generate
3. **What you see** when you open http://127.0.0.1:10000/v1/gallery
4. **What you see** when you open http://127.0.0.1:10000/docs

This will help me identify the exact issue!

---

*Troubleshooting Guide v1.0*  
*Created: 2025-09-30*
