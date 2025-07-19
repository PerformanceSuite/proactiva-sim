# 🎤 VAL Testing Guide

## 🌐 **Application is Now Running!**

### **Access Points:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎯 **How to Test VAL**

### **Step 1: Open the Application**
1. Go to **http://localhost:3000**
2. Look for the **"Ask VAL"** section with the large blue gradient box
3. You should see:
   - A large VAL avatar (blue circle with "V")
   - "Ask VAL 🎤" header
   - "Try These Commands" section with 6 example buttons
   - A large blue microphone button
   - Text input area

### **Step 2: Test Voice Input** 🎤
1. **Click the large blue microphone button** (round button with mic icon)
2. VAL should:
   - Turn red and show "🔴 Listening to your command..."
   - Display "Listening for your command..." overlay
3. **Say one of these commands:**
   - "Add 4 VR headsets"
   - "What's the current ROI?"
   - "Run simulation with 245 patients and 19 providers"
   - "Start the simulation"

### **Step 3: Test Text Input** ⌨️
1. **Click in the text area** (large white box)
2. **Type any of these commands:**
   - `Add 4 VR headsets`
   - `What's the current wait time?`
   - `If I add 6 more VR headsets, what would my wait time reduce to?`
3. **Click the green send button** or press Enter

### **Step 4: Test Quick Commands** 🚀
1. **Click any of the 6 blue example buttons:**
   - 🎯 Add 4 VR headsets
   - 📊 What's the current ROI?
   - 🏥 Run simulation with 245 patients and 19 providers
   - ▶️ Start the simulation
   - ⏰ What's the wait time?
   - 👥 Show provider utilization

## 🎭 **Expected VAL Behavior**

### **Visual States:**
- **🔵 Idle**: Blue gradient avatar, ready
- **🔴 Listening**: Red pulsing avatar with ripple effects
- **🟡 Thinking**: Yellow spinning avatar with bouncing dots
- **🟢 Speaking**: Green bouncing avatar with sound waves

### **Expected Responses:**
```
User: "Add 4 VR headsets"
VAL: "I've added 4 VR stations. You now have 6 VR therapy stations. Based on historical data, this could reduce wait times by approximately 10.0 minutes and improve patient satisfaction by 12.0%."

User: "What's the current ROI?"
VAL: "Current VR therapy ROI analysis: With 2 stations costing $30,000 annually, you're saving approximately $34,000 through improved patient experience and reduced traditional therapy costs. Your ROI is 13.3% annually."

User: "Run simulation with 245 patients and 19 providers"
VAL: "I'm starting a new simulation with 245 patients and 19 providers. This configuration should result in approximately 12.5 minute average wait times."
```

## 🔧 **Troubleshooting**

### **If you don't see VAL:**
1. Refresh the page (Ctrl+F5 or Cmd+Shift+R)
2. Check browser console for errors (F12)
3. Ensure you're on the AI Simulation tab/page

### **If microphone doesn't work:**
1. Check browser permissions (allow microphone access)
2. Use Chrome, Firefox, or Safari (best support)
3. Try text input instead - all features work via text

### **If no response from VAL:**
1. Check that backend is running: http://localhost:8000/docs
2. Look for error messages in the VAL interface
3. Try the fallback commands that work without simulation

## 🎯 **Success Indicators**

✅ **VAL interface is visible with blue gradient background**  
✅ **Large microphone button is present and clickable**  
✅ **Voice recognition activates (red state)**  
✅ **VAL provides intelligent responses**  
✅ **Simulation parameters change based on commands**  
✅ **Audio responses play back (if enabled)**  

---

## 🎉 **You're Ready to Test!**

**VAL is now fully operational as your Virtual Assistant for Leaders!**

*Try commanding VAL to add VR headsets, run simulations, or analyze ROI - all through natural voice or text interaction!*