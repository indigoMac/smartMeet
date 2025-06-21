# 🧪 Professional Outlook Add-in Testing Guide

## 🎯 Professional Development Workflow

This is how Outlook add-ins are tested professionally in real development environments.

### Prerequisites

- ✅ Development server running on `https://localhost:3001`
- ✅ Office 365 account (work or personal)
- ✅ Outlook web access

## 🚀 Method 1: Outlook Web (Recommended)

### Step 1: Start Development Server

```bash
# From project root
cd apps/outlook-addin && npm run start
```

Your add-in is now running at: https://localhost:3001

### Step 2: Manual Sideloading

1. **Open Outlook Web**: https://outlook.office.com
2. **Sign in** with your Office 365 account
3. **Open Settings**:
   - Click gear icon (⚙️) in top right
   - Select "View all Outlook settings"
4. **Navigate to Add-ins**:
   - Go to "General" → "Manage add-ins"
   - Click "Add a custom add-in"
   - Select "Add from file"
5. **Upload Manifest**:
   - Upload `manifest-dev.xml` from this directory
   - Click "Install"

### Step 3: Test Your Add-in

1. **Open any email** in Outlook web
2. **Look for your add-in**:
   - In the email toolbar, look for "SmartMeet DEV"
   - Click "Schedule Meeting" button
3. **Your add-in opens** in a side panel
4. **Live Development**: Any code changes will appear after refreshing the add-in panel

## 🖥️ Method 2: Outlook Desktop (Advanced)

### Manual Installation Process:

1. **Open Outlook Desktop**
2. **Go to File → Manage Add-ins**
3. **Click "My add-ins"**
4. **Select "Add a custom add-in" → "Add from file"**
5. **Upload** `manifest-dev.xml`

### Note on Desktop Development:

- Desktop requires manual refresh after code changes
- Web version is preferred for development
- Desktop testing is important before production

## 🔄 Live Development Workflow

### How Live Changes Work:

1. **Make code changes** in your editor
2. **Webpack automatically rebuilds** (watch the terminal)
3. **Refresh the add-in panel** in Outlook
4. **See your changes instantly**

### Example Development Cycle:

```bash
# 1. Edit your React component
# apps/outlook-addin/src/taskpane/taskpane.tsx

# 2. Save the file (Webpack rebuilds automatically)
# ✅ webpack compiled successfully

# 3. In Outlook web, refresh the add-in panel
# 4. See your changes immediately!
```

## 🧪 Testing Scenarios

### 1. **Email Reading**

- Open any email
- Click your add-in button
- Test functionality with email data

### 2. **Email Composition**

- Compose new email
- Your add-in should appear in compose mode
- Test meeting scheduling features

### 3. **Calendar Integration**

- Test calendar access
- Verify meeting creation
- Check attendee management

## 🔧 Professional Development Tips

### Hot Reload Setup:

```javascript
// In your React components, changes auto-reload
// No need to restart the server for code changes

// For manifest changes, you need to:
// 1. Update manifest-dev.xml
// 2. Re-upload to Outlook
// 3. Refresh browser
```

### Debugging:

```javascript
// Use browser dev tools
console.log("Debug info:", data);

// Office.js debugging
Office.onReady(() => {
  console.log("Office.js ready");
});
```

### Error Handling:

```javascript
// Professional error handling
try {
  const result = await Office.context.mailbox.item.subject.getAsync();
  console.log("Email subject:", result.value);
} catch (error) {
  console.error("Office.js error:", error);
}
```

## 🚨 Troubleshooting

### "Add-in won't load"

1. Check HTTPS certificate: `curl -k https://localhost:3001`
2. Verify manifest: `npm run validate`
3. Check browser console for errors

### "Office.js not available"

1. Ensure you're testing in Outlook (not regular browser)
2. Check manifest permissions
3. Verify Office.js script loads

### "Changes not appearing"

1. Hard refresh the add-in panel (Ctrl+F5)
2. Check webpack compilation in terminal
3. Clear browser cache if needed

## 📱 Testing Across Platforms

### Priority Order:

1. **Outlook Web** (Primary development)
2. **Outlook Desktop** (Windows/Mac)
3. **Outlook Mobile** (Final testing)

### Professional Testing Matrix:

- ✅ Chrome + Outlook Web
- ✅ Edge + Outlook Web
- ✅ Outlook Desktop (Windows)
- ✅ Outlook Desktop (Mac)
- ✅ Outlook Mobile (iOS/Android)

## 🔐 Account Integration

### How Outlook Knows Your Account:

- **Outlook Web**: Uses your browser session
- **Outlook Desktop**: Uses Windows/Mac credentials
- **Add-in Context**: Automatically inherits user context

### Accessing User Data:

```javascript
// Get current user
Office.context.mailbox.userProfile.emailAddress;

// Get current email
Office.context.mailbox.item.subject.getAsync();

// Get attendees
Office.context.mailbox.item.to.getAsync();
```

## 🎉 You're Ready!

Your professional development setup is complete:

- ✅ Live code changes
- ✅ Professional debugging
- ✅ Multi-platform testing
- ✅ Office.js integration

**Next**: Upload `manifest-dev.xml` to Outlook web and start developing!
