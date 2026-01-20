# 🔧 HOW TO DISABLE EMAIL VERIFICATION

## ✅ WHAT TO DO IN RENDER:

1. **Go to:** Render Dashboard → Your Service → Environment

2. **Find:** `ENABLE_EMAIL_VERIFICATION`

3. **Change value to:** `false`

4. **Click:** "Save Changes"

5. **Wait:** 2-3 minutes for redeploy

---

## ✅ RESULT:

- ✅ Users can sign up and login immediately
- ✅ No email verification needed
- ✅ App works perfectly

---

## 📋 YOUR ENVIRONMENT VARIABLE:

```
ENABLE_EMAIL_VERIFICATION=false
```

---

## 🎯 WHEN YOU'RE READY TO ADD EMAIL BACK:

1. **Upgrade Render** to paid tier ($7/month) - unblocks SMTP ports
2. **OR use an HTTP API** email service (not SMTP)
3. **Change back to:** `ENABLE_EMAIL_VERIFICATION=true`

---

That's it! Simple and clean! 🚀

