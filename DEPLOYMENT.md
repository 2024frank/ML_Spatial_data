# 🚀 Deployment Guide for Purple Air Sensor Dashboard

This guide shows you how to deploy your Purple Air sensor dashboard to the cloud securely.

## 🎯 **Option 1: Streamlit Community Cloud (Recommended)**

### **Step 1: Prepare Your Repository**

Your repository is already prepared! The code automatically handles both local and cloud deployment.

### **Step 2: Deploy to Streamlit Cloud**

1. **Go to [share.streamlit.io](https://share.streamlit.io/)**
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Select your repository**: `2024frank/ML_Spatial_data`
5. **Branch**: `main`
6. **Main file path**: `streamlit_dashboard.py`
7. **Click "Deploy"**

### **Step 3: Configure Secrets**

1. **In Streamlit Cloud**, go to your app settings
2. **Click "Secrets"** in the sidebar
3. **Copy your `credentials.json` content**
4. **Add these secrets**:

```toml
SPREADSHEET_ID = "1KLwB85EZK1WvCCh5iWtkl2gxd_4B__jRWsdDoU1fjs0"
SHEET_RANGE = "PurpleAir002_AJLC Building!A:Z"
SENSOR_LAT = "41.29075599398253"
SENSOR_LON = "-82.22151197237143"
SENSOR_NAME = "AJLC Building Purple Air Sensor"

google_credentials = '''
{
  "type": "service_account",
  "project_id": "airquality-466023",
  "private_key_id": "your-actual-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR-ACTUAL-PRIVATE-KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "airquality@airquality-466023.iam.gserviceaccount.com",
  "client_id": "your-actual-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/airquality%40airquality-466023.iam.gserviceaccount.com"
}
'''
```

### **Step 4: Save and Deploy**

1. **Click "Save"**
2. **Your app will automatically redeploy**
3. **Access your live dashboard** at your Streamlit Cloud URL!

---

## 🎯 **Option 2: Heroku Deployment**

### **Step 1: Create Heroku App**

```bash
# Install Heroku CLI first
heroku create your-purple-air-app
```

### **Step 2: Add Buildpacks**

```bash
heroku buildpacks:add heroku/python
```

### **Step 3: Set Environment Variables**

```bash
heroku config:set SPREADSHEET_ID="1KLwB85EZK1WvCCh5iWtkl2gxd_4B__jRWsdDoU1fjs0"
heroku config:set SHEET_RANGE="PurpleAir002_AJLC Building!A:Z"
heroku config:set SENSOR_LAT="41.29075599398253"
heroku config:set SENSOR_LON="-82.22151197237143"
heroku config:set SENSOR_NAME="AJLC Building Purple Air Sensor"

# Set Google credentials as a single JSON string
heroku config:set GOOGLE_CREDENTIALS='{"type":"service_account",...}'
```

### **Step 4: Create Procfile**

```bash
echo "web: streamlit run streamlit_dashboard.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

### **Step 5: Deploy**

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

---

## 🎯 **Option 3: Docker Deployment**

### **Step 1: Create Dockerfile**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.address=0.0.0.0"]
```

### **Step 2: Build and Run**

```bash
# Build image
docker build -t purple-air-dashboard .

# Run container with environment variables
docker run -p 8501:8501 \
  -e SPREADSHEET_ID="your-sheet-id" \
  -e GOOGLE_CREDENTIALS='{"type":"service_account",...}' \
  purple-air-dashboard
```

---

## 🔐 **Security Best Practices**

### **✅ What We Already Did Right:**

1. **`.gitignore`** - Excludes `credentials.json` from Git
2. **Environment Variables** - Uses secure configuration methods
3. **Secrets Management** - Streamlit secrets for cloud deployment
4. **Code Separation** - Configuration separate from code

### **🛡️ Additional Security:**

1. **Rotate Credentials** - Change service account keys periodically
2. **Limit Permissions** - Service account has only "Viewer" access to sheets
3. **Monitor Access** - Check Google Cloud audit logs
4. **Use HTTPS** - All deployment platforms use HTTPS by default

---

## 🌐 **Custom Domain (Optional)**

### **For Streamlit Cloud:**
- Available in paid plans
- Set up through your app settings

### **For Other Platforms:**
- Configure your domain DNS to point to the deployment URL
- Set up SSL certificates (usually automatic)

---

## 📊 **Monitoring Your Deployed App**

### **Streamlit Cloud:**
- Built-in logs and metrics
- Email notifications for downtime

### **Heroku:**
- Use `heroku logs --tail` for live logs
- Add monitoring add-ons like New Relic

### **Docker:**
- Use container orchestration tools
- Set up health checks and monitoring

---

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **"Secrets not found"**
   - Check secrets formatting in Streamlit Cloud
   - Ensure all required secrets are set

2. **"Authentication failed"**
   - Verify Google credentials are correct
   - Check service account has access to spreadsheet

3. **"Module not found"**
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version compatibility

4. **"App won't start"**
   - Check logs for specific error messages
   - Verify port configuration for your platform

---

## ✅ **Deployment Checklist**

- [ ] Repository pushed to GitHub
- [ ] Secrets configured (never commit credentials!)
- [ ] App deployed to chosen platform
- [ ] Dashboard loads and shows data
- [ ] All features working (maps, charts, analysis)
- [ ] Error monitoring set up
- [ ] Domain configured (if needed)

---

**🎉 Your Purple Air sensor dashboard is now live and accessible from anywhere!**

**Example URLs:**
- Streamlit Cloud: `https://your-app-name.streamlit.app`
- Heroku: `https://your-purple-air-app.herokuapp.com`
- Custom: `https://your-domain.com` 