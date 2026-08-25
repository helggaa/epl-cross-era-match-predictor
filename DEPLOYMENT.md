# 🚀 100% Free Forever Deployment Guide

This guide walks you through deploying the **EPL Cross-Era Match Predictor** with **$0/month forever hosting**:

| Component | Service | Free Tier Details |
|---|---|---|
| **Frontend** | **Cloudflare Pages** | Unlimited bandwidth, global edge CDN, 100% free forever |
| **Backend** | **Render (Web Service)** | 512 MB RAM, 750 free instance hours/month |
| **Database** | **SQLite (Bundled)** | Embedded inside container, zero database cost |

---

## 📋 Step 1: Push Project to GitHub

Make sure all your latest changes are pushed to your GitHub repository:

```bash
git add .
git commit -m "chore: prepare for Cloudflare Pages and Render deployment"
git push origin main
```

---

## 🖥️ Step 2: Deploy Backend to Render

1. Go to [Render.com](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** -> **Web Service**.
3. Select **Build and deploy from a Git repository** and pick your `EPL_allTime_predict` repository.
4. Fill in the deployment details:
   - **Name**: `epl-predictor-backend` (or any name you like)
   - **Language / Runtime**: `Docker`
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Instance Type**: **Free** ($0/month)
5. Under **Environment Variables**, add:
   - `CORS_ORIGINS`: `*`
   - `DATABASE_URL`: `sqlite:///./epl_predictor.db`
   - *(Optional)* `GEMINI_API_KEY`: `your_gemini_api_key` (if using AI pundit breakdown)
6. Click **Create Web Service**.
7. Once deployed, copy your backend URL (e.g. `https://epl-predictor-backend.onrender.com`).
8. Verify it by visiting: `https://epl-predictor-backend.onrender.com/api/v1/health` in your browser.

> [!NOTE]
> Render free web services spin down after 15 minutes of inactivity. When accessed after being idle, the first request will take ~30-50 seconds to wake up (cold start), then perform quickly.

---

## ⚡ Step 3: Deploy Frontend to Cloudflare Pages

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/) and navigate to **Workers & Pages** -> **Create application** -> **Pages** -> **Connect to Git**.
2. Select your `EPL_allTime_predict` repository.
3. Configure the build settings:
   - **Framework preset**: `Vite`
   - **Root directory**: `frontend`
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
4. Under **Environment variables (advanced)**, add:
   - Variable name: `VITE_API_BASE_URL`
   - Value: `https://your-render-backend-url.onrender.com/api/v1` *(replace with your actual Render URL from Step 2)*
5. Click **Save and Deploy**.
6. Cloudflare will build and give you a public URL (e.g. `https://epl-cross-era-match-predictor.pages.dev`).

---

## 🧪 Step 4: Test Your Live App

1. Open your Cloudflare Pages URL in your browser.
2. Select any two iconic teams (e.g. *Arsenal 2003-04* vs *Manchester City 2017-18*).
3. Click **Simulate Match** and verify the prediction probabilities, scoreline distribution, and AI pundit analysis.

---

## 🛠️ Maintenance & Future Updates

- **Automatic Deployments**: Any time you `git push` to your `main` branch, Cloudflare Pages and Render will automatically rebuild and deploy your changes.
- **Custom Domains (Optional & Free)**: Both Cloudflare Pages and Render allow you to link your own custom domain (e.g., `eplmatchpredictor.com`) for free with automatic SSL.
