# 🔧 Fix Database Connection - Simple Step-by-Step Guide

## What's Wrong?
Your app can't find the database because the database address is incomplete. It's like having a phone number without the area code.

## Step 1: Go to Your Render Dashboard
1. Open your web browser
2. Go to: https://dashboard.render.com
3. Log in to your account

## Step 2: Find Your Database
1. Look on the left side menu
2. Click on **"PostgreSQL"** (or look for a database named "skileez-db")
3. Click on your database name

## Step 3: Check if Database is Paused
1. Look at the top of the database page
2. If you see a button that says **"Resume"** or **"Wake"**, click it
3. Wait 30-60 seconds for the database to start

## Step 4: Get the Correct Database Address
1. Scroll down on the database page
2. Look for a section called **"Connections"** or **"Connection Info"**
3. You'll see two connection strings:
   - **Internal Connection String** (for services in same region)
   - **External Connection String** (for services from outside)
   
4. **Copy the EXTERNAL Connection String** (it should have `.oregon-postgres.render.com` or similar domain in it)

## Step 5: Update Your Web Service Database URL
1. Go back to the main dashboard (click "Dashboard" on the left)
2. Click on your **Web Service** (the one running your app, usually named "skileez")
3. Click on the **"Environment"** tab (or look for "Environment Variables")
4. Find the variable called **"DATABASE_URL"**
5. Click on it to edit
6. **Replace** the old value with the **External Connection String** you copied
7. Click **"Save Changes"**

## Step 6: Restart Your Service
1. Go to the **"Events"** or **"Logs"** tab
2. Look for a button that says **"Manual Deploy"** or **"Restart"**
3. Click it to restart your service
4. Wait 2-3 minutes for it to restart

## Step 7: Test Again
1. Go to your website: https://skileez-gol.onrender.com/admin/login
2. Enter password: `admin123`
3. It should work now!

## If It Still Doesn't Work

### Check 1: Is the database URL correct?
- It should start with: `postgresql://`
- It should have a domain like: `.oregon-postgres.render.com` or `.singapore-postgres.render.com`
- Example format: `postgresql://user:password@dpg-xxx-a.oregon-postgres.render.com/dbname`

### Check 2: Is the database running?
- Go back to your database page
- Make sure it says "Available" or "Running" (not "Paused")

### Check 3: Check the logs
- Go to your web service
- Click "Logs" tab
- Look for any new error messages
- Share them if you see any errors

## Quick Checklist
- [ ] Database is not paused
- [ ] Used External Connection String (has domain name)
- [ ] Updated DATABASE_URL environment variable
- [ ] Restarted the web service
- [ ] Waited 2-3 minutes for restart

## Need Help?
If you're stuck, share:
1. What step you're on
2. What you see on your screen
3. Any error messages

