# Registration Flow - Complete Visual Guide with Screenshots

## 🎯 Current State
You're on: **http://localhost:4321** (Home Page)

The home page shows:
```
Upcoming Sports Events
└── Jakarta Marathon 2026 →
```

---

## 🚀 Step 1: Navigate to Event Registration Page

### What You See Now:
```
Home Page at http://localhost:4321
├── Title: "Upcoming Sports Events"
└── Link: "Jakarta Marathon 2026 →"
```

### What to Do:
**Click on "Jakarta Marathon 2026 →"**

This will take you to: **http://localhost:4321/events/event-register**

---

## 📄 Step 2: Event Registration Page (After Clicking)

### Expected Page Structure:

```
┌─────────────────────────────────────────────────────────────┐
│                 Event Details Section                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Event Banner Image]                                         │
│  ╔════════════════════════════════════════════════════════╗  │
│  ║  Jakarta Marathon 2026                                 ║  │
│  ╚════════════════════════════════════════════════════════╝  │
│                                                               │
│  📅 November 15, 2026                                        │
│  📍 Jakarta, Indonesia                                        │
│                                                               │
│  Join thousands of runners for an exciting marathon          │
│  experience in Jakarta.                                      │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                   Registration Form                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Register Now                                                │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Full Name *                                          │  │
│  │ [input field: "John Doe"]                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Email Address *                                      │  │
│  │ [input field: "john@example.com"]                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Phone Number (Optional)                              │  │
│  │ [input field: "+1234567890"]                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         [Register Now Button]                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  We'll never share your information. See our privacy        │
│  policy.                                                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Step 3: Fill the Registration Form

### Form Fields:

**1. Full Name (Required)**
```
Label: "Full Name *"
Type: Text input
Placeholder: "John Doe"
Validation: 
  - Required (not empty)
  - Min 2 characters
  - Max 100 characters
Error Message (if invalid): 
  ⚠️ Full name must be at least 2 characters
```

**2. Email Address (Required)**
```
Label: "Email Address *"
Type: Email input
Placeholder: "john@example.com"
Validation:
  - Required (not empty)
  - Valid email format (contains @ and .)
Error Messages (if invalid):
  ⚠️ Email is required
  ⚠️ Please enter a valid email address
```

**3. Phone Number (Optional)**
```
Label: "Phone Number (Optional)"
Type: Tel input
Placeholder: "+1 (555) 123-4567"
Validation:
  - Optional (can be empty)
  - If provided: 10+ digits
Error Message (if invalid):
  ⚠️ Please enter a valid phone number (at least 10 digits)
```

### Example Valid Input:
```
Full Name: "John Doe"
Email: "john@example.com"
Phone: "+1 (555) 123-4567"
```

---

## ✅ Step 4: Submit Form

### What Happens:

**1. Client-Side Validation (Instant)**
```
Check:
✓ Full Name not empty
✓ Full Name length OK
✓ Email format valid
✓ Phone format valid (if provided)

If any error → Show red error messages next to fields
If all valid → Continue to step 2
```

**2. Submit Button States**
```
State: "idle" (Initial)
└─ Button: Blue, "Register Now"

State: "submitting" (After click)
└─ Button: Gray, "⏳ Submitting...", Disabled

State: "processing" (Waiting for confirmation)
└─ Button: Gray, "⏳ Processing...", Disabled

State: "success" (After confirmation)
└─ Modal appears (see next section)

State: "error" (If failed)
└─ Button: Blue, "Try Again"
└─ Error message shown below button
```

### Loading States Visual:

```
┌─ Submitting State ─────────────────────────┐
│                                             │
│  Form visible with fields disabled:         │
│                                             │
│  Full Name: [DISABLED]                      │
│  Email: [DISABLED]                          │
│  Phone: [DISABLED]                          │
│                                             │
│  [⏳ Submitting...]  ← Gray button          │
│                                             │
│  ℹ️ Registration submitted. Waiting for     │
│     confirmation...                         │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🎉 Step 5: Confirmation Modal (After SSE Event)

### Beautiful Success Modal Appears:

```
┌─────────────────────────────────────────────────────────────┐
│  ✓ Registration Confirmed!                                  │
│  You're all set for Jakarta Marathon 2026                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Name:              John Doe                           │  │
│  │ Email:             john@example.com                   │  │
│  │ Phone:             +1 (555) 123-4567                  │  │
│  │ Status:            ✓ confirmed                        │  │
│  │ Confirmation ID:   uuid-1234-5678-abcd-efgh           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ℹ️ A confirmation email has been sent to              │  │
│  │    john@example.com. Please check your inbox for      │  │
│  │    event details.                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              [Close]  [Print Confirmation]            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Modal Features:

**1. Success Icon** ✓
```
Green checkmark in a green circle
Indicates successful registration
```

**2. Registration Details Box**
```
Name:              [Full name entered]
Email:             [Email entered]
Phone:             [Phone entered if provided]
Status:            ✓ confirmed (green badge)
Confirmation ID:   [UUID - unique identifier]
```

**3. Info Message**
```
"A confirmation email has been sent to john@example.com.
Please check your inbox for event details."
```

**4. Action Buttons**
```
[Close] - Closes the modal, clears form
[Print Confirmation] - Opens print dialog for confirmation
```

---

## 🔄 Step-by-Step Visual Flow

```
STEP 1: Home Page
│
├─ URL: http://localhost:4321
├─ Shows: "Upcoming Sports Events"
│         "Jakarta Marathon 2026 →"
│
▼
Click "Jakarta Marathon 2026 →"
│
▼
STEP 2: Event Details Page
│
├─ URL: http://localhost:4321/events/event-register
├─ Shows: Event image/banner
│         Event title, date, location
│         Description
│         Registration form
│
▼
Fill Form:
│
├─ Full Name: "John Doe"
├─ Email: "john@example.com"
├─ Phone: "+1234567890"
│
▼
Click "Register Now"
│
├─ Client validates form (check: not empty, valid email, etc.)
│ └─ If errors: Show red error messages, Stop
│ └─ If valid: Continue...
│
▼
STEP 3: Submitting
│
├─ Button shows: "⏳ Submitting..."
├─ POST /api/v1/registrations
│ └─ Sends: {event_id, full_name, email, phone}
│ └─ Response: {registration_id, status: "pending"}
│
▼
STEP 4: Processing
│
├─ Button shows: "⏳ Processing..."
├─ Open EventSource connection
├─ Wait for Kafka to process
├─ Message: "Registration submitted. Waiting for confirmation..."
│
▼
STEP 5: SSE Event Received
│
├─ Event: registration_update
├─ Data: {registration_id, status: "confirmed", message: "...!"}
├─ State changes to: "success"
│
▼
STEP 6: Success Modal Appears! 🎉
│
├─ Show confirmation modal
├─ Display all details:
│  ├─ Name: John Doe
│  ├─ Email: john@example.com
│  ├─ Phone: +1234567890
│  ├─ Status: ✓ confirmed
│  └─ ID: uuid-1234-5678
├─
├─ Options:
│  ├─ [Close] button
│  └─ [Print Confirmation] button
│
▼
User Interaction
│
├─ Click [Close]
│  └─ Modal closes, form resets
│     User can register again
│
├─ Click [Print Confirmation]
│  └─ Opens print dialog
│     User can print confirmation
│     Modal stays open
│
```

---

## 🎨 Visual States Summary

### 1️⃣ Initial State
```
Form is visible, all fields empty
Button: Blue "Register Now"
No errors shown
```

### 2️⃣ Validation Error State
```
Some field has invalid data
Error message appears in red below field
Example:
  Email: [john@invalid]  ← Red border
  ⚠️ Please enter a valid email address  ← Red text
```

### 3️⃣ Submitting State
```
Form visible but all inputs disabled
Button: Gray "⏳ Submitting..."
Info message: "Registration submitted. Waiting for confirmation..."
```

### 4️⃣ Processing State
```
Form visible but all inputs disabled
Button: Gray "⏳ Processing..."
Info message: "Registration submitted. Waiting for confirmation..."
SSE connection open, listening for updates
```

### 5️⃣ Success State (Modal)
```
Modal overlay appears (semi-transparent background)
Modal shows:
  ✓ Registration Confirmed!
  All registration details
  Success message
  Action buttons
```

### 6️⃣ Error State
```
Form visible
Button: Blue "Try Again"
Error alert box shown:
  ❌ Registration Error
  [Error message details]
```

---

## 📱 Responsive Design

### Desktop (1024px+)
```
Full-width form with nice padding
Image and text side-by-side
Modal centered on screen
```

### Tablet (768px-1023px)
```
Slightly narrower form
Image full-width
Modal takes 80% of screen width
```

### Mobile (< 768px)
```
Full-width form
Image full-width
Modal takes 100% width with padding
Touch-friendly button sizes
Stacked layout
```

---

## 🔧 What Happens Behind the Scenes

### Network Requests:

**Request 1: POST Registration**
```
POST http://localhost:8000/api/v1/registrations
Content-Type: application/json

Body:
{
  "event_id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}

Response (202 Accepted):
{
  "registration_id": "uuid-1234-5678",
  "event_id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "status": "pending"
}

Status Code: 202 Accepted
```

**Request 2: SSE Stream**
```
GET http://localhost:8000/api/v1/sse/registrations/uuid-1234-5678
Accept: text/event-stream

Waits for Kafka processing...

Response (after ~5-10 seconds):
event: registration_update
data: {"registration_id":"uuid-1234-5678","status":"confirmed","message":"Registration confirmed!"}
```

---

## ✨ Features Demonstrated

✅ **Real-time Updates** - SSE shows live confirmation  
✅ **Form Validation** - Client-side error checking  
✅ **Loading States** - Button feedback during processing  
✅ **Error Handling** - Specific error messages  
✅ **Beautiful Modal** - Confirmation popup  
✅ **Print Support** - Can print confirmation  
✅ **Responsive** - Works on mobile, tablet, desktop  
✅ **Accessibility** - ARIA labels, semantic HTML  

---

## 🎬 Quick Summary

1. **Click** "Jakarta Marathon 2026 →" on home page
2. **Fill** the registration form (name, email, phone)
3. **Click** "Register Now" button
4. **See** loading states (Submitting... → Processing...)
5. **Wait** for SSE confirmation (~5-10 seconds)
6. **See** beautiful confirmation modal 🎉
7. **Click** Close or Print Confirmation

---

## 🐛 Troubleshooting

### Form doesn't appear
```
❌ Make sure you're at: http://localhost:4321/events/event-register
✅ Not at: http://localhost:4321 (home page)
```

### Registration fails
```
❌ Check if registration service is running:
   curl http://localhost:8000/health

✅ Should show: {"status":"ok"}
```

### Modal doesn't appear
```
❌ Check browser console (F12) for errors
❌ Make sure Kafka is running (docker-compose logs)

✅ Wait 5-10 seconds for processing
✅ Check Network tab in F12 for SSE connection
```

### Form stuck on "Processing..."
```
❌ Page might have crashed silently
✅ Refresh the page (F5)
✅ Try again with different email
```

---

## 📞 Contact Info Display in Modal

When the modal shows, you'll see all the data you entered:

```
Name:              Exactly what you typed
Email:             Lowercased version
Phone:             Trimmed version
Status:            ✓ confirmed (from server)
Confirmation ID:   Unique UUID from server
```

Plus a message:
```
"A confirmation email has been sent to your.email@example.com.
Please check your inbox for event details."
```

---

