# Elecantro User Guide 🚀

Welcome to **Elecantro**, your AI-powered feedback analysis platform. This guide will walk you through the application from start to finish.

---

## 0. Developer Setup (IMPORTANT!)

Before using the application, you need to start **two** services:

### Terminal 1: Django Server
```bash
cd backend
.venv\Scripts\activate
python manage.py runserver
```

### Terminal 2: Background Worker (Required for File Processing!)
```bash
cd backend
start_worker.bat
```
**OR manually:**
```bash
cd backend
.venv\Scripts\activate
celery -A core worker -l info -P eventlet
```

> **⚠️ Critical:** Without the background worker running, uploaded files will get stuck at "Processing 0%". The worker handles AI analysis in the background.

### Terminal 3: Frontend (if not already running)
```bash
cd frontend
npm run dev
```

---

## 1. Getting Started

### Registration
1. Open the application in your browser (usually `http://localhost:5173`).
2. Click **"Sign Up"** if you don't have an account.
3. Fill in your details:
   - **First & Last Name**: Your personal details.
   - **Username**: Unique identifier for login.
   - **Work Email**: Your professional email address.
   - **Company Name**: Your organization's name.
   - **Password**: Create a secure password.
4. Click **"Get Started"** to create your account.

### Login
1. Once registered, you will be redirected to the Login page.
2. Enter your **Username** (or Email) and **Password**.
3. Click **"Sign In"**.
4. You will land on the **Dashboard Overview**.

---

## 2. Setting Up Your Workspace

Before analyzing data, you need a "Business Entity" (a workspace for your brand or client).

1. Navigate to **Ingestion Hub** in the sidebar menu.
2. Look for the dropdown menu at the top right labeled **"Select Business:"**.
3. If it says **"No entities found"**, click the **"+ New"** button next to it.
4. Enter a unique name for your business (e.g., "Acme Corp Returns").
5. Click **"Save"**.
6. The system will automatically select your new entity.

> **Note:** You only need to do this once per project. You can switch between entities anytime using the dropdown.

---

## 3. Uploading Feedback Data

Now, let's feed the AI some data!

1. Stay on the **Ingestion Hub** page.
2. Prepare your data file. Supported formats: **CSV** (`.csv`) or **Excel** (`.xlsx`).
   - **Requirement**: Your file *must* have a column named `text` (or `review`, `comment`) containing the feedback.
   - *Tip: A sample file `sample_reviews.xlsx` is available in the backend folder.*
3. Click **"Browse Files"** or drag and drop your file into the upload area.
4. The upload will start immediately.
5. Watch the **Recent Uploads** section at the bottom.
   - You will see a progress bar indicating the AI processing status.
   - Statuses: `Uploading` -> `Processing` -> `Completed`.

---

## 4. Viewing Results

Once the upload status says **"Completed"**, your insights are ready!

### Dashboard Overview
Click **"Overview"** in the sidebar. This is your command center.
- **KPI Cards**: See Total Feedback count, Average Sentiment, and Critical Issues at a glance.
- **Sentiment Trend**: Visual graph showing how sentiment changes over time.
- **Sentiment Breakdown**: Pie chart of Positive vs. Negative feedback.
- **Top Topics**: Automatic categorization of what customers are talking about (e.g., "Billing", "Performance").
- **Product Performance**: If your data includes product names, compare them here.

### Deep Dive Insights
Click **"Insights AI"** in the sidebar. This is your detailed explorer.
- **Search**: Type to find specific feedback text or topics.
- **Filters**: quickly view only **Negative** feedback or **High Urgency** items.
- **Analysis Cards**: Each card shows:
  - **Sentiment**: (Positive/Neutral/Negative) with a confidence score.
  - **Urgency Tags**: Identifies if a review needs immediate attention (e.g., "Critical Priority").
  - **Topics**: Auto-tagged keywords.
  - **Text**: The original customer review.

---

## 5. Troubleshooting

- **Upload Failed?** Check that your CSV/Excel file has a `text` column.
- **No Data in Dashboard?** Ensure your upload batch shows as "Completed" in the Ingestion Hub.
- **Cannot Create Entity?** The name must be unique across the system. Try adding a number or specific identifier (e.g., "My Brand 2024").

---

**Enjoy using Elecantro!**
