# Phase 5: Journey Management in Settings - Test Plan

## Test Date
December 31, 2025

## Test Scope
Testing journey management UI in Settings page - add, remove, switch journeys

---

## 1. Settings Page Integration Tests

### 1.1 Journey Management Section Visible
**URL:** http://localhost:3000/settings

**Prerequisites:** User logged in with at least one journey

**Visual Checks:**
- [ ] "Learning Journeys" section appears in Settings
- [ ] Section positioned between Account and Appearance
- [ ] Header shows "Learning Journeys" title
- [ ] Description text visible
- [ ] "Add Journey" button visible (if < 4 journeys)

**Result:** ✅ PASS / ❌ FAIL

---

### 1.2 Journey Cards Display
**Test:** Verify all active journeys display correctly

**Visual Checks:**
- [ ] Each journey shows as a card
- [ ] Journey icon displayed with correct color background
- [ ] Journey name and description visible
- [ ] "Active" badge on current journey
- [ ] "Primary" badge on primary journey
- [ ] Level badge with journey color
- [ ] Progress stats (lessons, XP) displayed
- [ ] Progress bar at bottom of card
- [ ] Switch button on non-active journeys
- [ ] Remove button on all journeys (if > 1)

**Result:** ✅ PASS / ❌ FAIL

---

## 2. Add Journey Tests

### 2.1 Open Add Journey Modal
**Test:** Click "Add Journey" button

**Expected:**
- [ ] Modal opens with overlay
- [ ] Modal title: "Add New Journey"
- [ ] Close button (X) visible
- [ ] Available journey types displayed (not already added)
- [ ] Journey type cards show icon, name, description

**Result:** ✅ PASS / ❌ FAIL

---

### 2.2 Select Journey Type
**Test:** Click on a journey type card

**Expected:**
- [ ] Selected card highlights (blue border)
- [ ] Level selection section appears
- [ ] Levels displayed based on journey type
  - Student: A1, A2, B1, B2, C1
  - Others: Beginner, Intermediate, Advanced

**Result:** ✅ PASS / ❌ FAIL

---

### 2.3 Select Level
**Test:** Click on a level button

**Expected:**
- [ ] Selected level highlights (blue border)
- [ ] "Add Journey" button becomes enabled
- [ ] No error messages

**Result:** ✅ PASS / ❌ FAIL

---

### 2.4 Add Journey - Success
**Test:** Complete journey addition

**Steps:**
1. Click "Add Journey"
2. Select "Traveler" journey
3. Select "Beginner" level
4. Click "Add Journey" button

**Expected:**
- [ ] Button shows "Adding..." during request
- [ ] Modal closes on success
- [ ] New journey card appears in list
- [ ] Journey shows correct icon, name, level
- [ ] No error messages

**Result:** ✅ PASS / ❌ FAIL

---

### 2.5 Add Journey - Validation
**Test:** Try to add without selecting type/level

**Steps:**
1. Open modal
2. Click "Add Journey" without selections

**Expected:**
- [ ] Error message: "Please select a journey type and level"
- [ ] Modal stays open
- [ ] No journey added

**Result:** ✅ PASS / ❌ FAIL

---

### 2.6 Add Journey - Duplicate Prevention
**Test:** Try to add same journey type twice

**Steps:**
1. Add Student journey
2. Try to add Student journey again

**Expected:**
- [ ] Student journey not shown in available types
- [ ] Only unselected journey types visible
- [ ] Cannot add duplicate

**Result:** ✅ PASS / ❌ FAIL

---

### 2.7 Add Journey - Maximum Limit
**Test:** Add all 4 journey types

**Expected:**
- [ ] Can add up to 4 journeys
- [ ] "Add Journey" button hidden when all 4 added
- [ ] All 4 journey cards displayed

**Result:** ✅ PASS / ❌ FAIL

---

### 2.8 Cancel Add Journey
**Test:** Open modal and cancel

**Steps:**
1. Click "Add Journey"
2. Select journey type and level
3. Click "Cancel" or X button

**Expected:**
- [ ] Modal closes
- [ ] No journey added
- [ ] Selections reset
- [ ] No error messages

**Result:** ✅ PASS / ❌ FAIL

---

## 3. Switch Journey Tests

### 3.1 Switch to Different Journey
**Test:** Switch from Student to Traveler

**Steps:**
1. Have Student journey active
2. Click "Switch" on Traveler journey card

**Expected:**
- [ ] Active badge moves to Traveler
- [ ] Student card shows "Switch" button
- [ ] Traveler card no longer shows "Switch" button
- [ ] Dashboard updates to Traveler theme (verify by navigating)

**Result:** ✅ PASS / ❌ FAIL

---

### 3.2 Switch Between Multiple Journeys
**Test:** Rapid switching between 3+ journeys

**Steps:**
1. Have 3+ journeys
2. Switch: Student → Traveler → Professional → Student

**Expected:**
- [ ] Each switch updates active badge immediately
- [ ] No errors or delays
- [ ] UI updates correctly each time
- [ ] Dashboard reflects active journey

**Result:** ✅ PASS / ❌ FAIL

---

### 3.3 Switch Journey Persistence
**Test:** Switch journey and refresh page

**Steps:**
1. Switch to Professional journey
2. Refresh Settings page (F5)
3. Navigate to Dashboard and back

**Expected:**
- [ ] Professional journey still active after refresh
- [ ] Active badge persists
- [ ] Dashboard shows Professional theme

**Result:** ✅ PASS / ❌ FAIL

---

## 4. Remove Journey Tests

### 4.1 Remove Non-Active Journey
**Test:** Remove a journey that's not currently active

**Steps:**
1. Have Student (active) and Traveler journeys
2. Click "Remove" on Traveler journey
3. Confirm in dialog

**Expected:**
- [ ] Confirmation dialog appears
- [ ] Dialog message: "Are you sure you want to remove this journey? Your progress will be saved."
- [ ] Journey removed from list
- [ ] Active journey unchanged
- [ ] No errors

**Result:** ✅ PASS / ❌ FAIL

---

### 4.2 Remove Active Journey
**Test:** Remove the currently active journey

**Steps:**
1. Have Student (active) and Traveler journeys
2. Click "Remove" on Student journey
3. Confirm in dialog

**Expected:**
- [ ] Journey removed
- [ ] System automatically switches to remaining journey
- [ ] Remaining journey becomes active
- [ ] Dashboard updates to new active journey

**Result:** ✅ PASS / ❌ FAIL

---

### 4.3 Remove Last Journey - Prevention
**Test:** Try to remove when only 1 journey exists

**Steps:**
1. Have only Student journey
2. Click "Remove" button

**Expected:**
- [ ] Error message: "You must have at least one active journey"
- [ ] Journey not removed
- [ ] Error disappears after 3 seconds

**Result:** ✅ PASS / ❌ FAIL

---

### 4.4 Cancel Remove Journey
**Test:** Start remove but cancel

**Steps:**
1. Click "Remove" on a journey
2. Click "Cancel" in confirmation dialog

**Expected:**
- [ ] Dialog closes
- [ ] Journey not removed
- [ ] No changes to journey list

**Result:** ✅ PASS / ❌ FAIL

---

### 4.5 Remove Multiple Journeys
**Test:** Remove journeys one by one

**Steps:**
1. Have 4 journeys
2. Remove Hobby journey
3. Remove Professional journey
4. Remove Traveler journey
5. Try to remove Student (last one)

**Expected:**
- [ ] First 3 removals succeed
- [ ] Last removal blocked with error
- [ ] Student journey remains

**Result:** ✅ PASS / ❌ FAIL

---

## 5. Progress Display Tests

### 5.1 Progress Stats Accuracy
**Test:** Verify progress stats display correctly

**Check:**
- [ ] Lessons completed count accurate
- [ ] XP total accurate
- [ ] Progress bar percentage matches lessons/50
- [ ] Stats update after completing lessons

**Result:** ✅ PASS / ❌ FAIL

---

### 5.2 Progress Bar Visual
**Test:** Progress bar displays correctly

**Check:**
- [ ] Bar color matches journey color
- [ ] Bar width proportional to progress
- [ ] Percentage text accurate
- [ ] Bar animates smoothly
- [ ] 0% shows empty bar
- [ ] 100% shows full bar

**Result:** ✅ PASS / ❌ FAIL

---

## 6. UI/UX Tests

### 6.1 Dark Mode
**Test:** All journey management UI in dark mode

**Check:**
- [ ] Journey cards readable
- [ ] Modal background appropriate
- [ ] Text contrast sufficient
- [ ] Colors work in dark mode
- [ ] Buttons visible and styled correctly

**Result:** ✅ PASS / ❌ FAIL

---

### 6.2 Responsive Design
**Test:** Journey management on different screens

**Screen Sizes:**
- [ ] Desktop (1920x1080) - Cards side by side
- [ ] Laptop (1366x768) - Cards stack properly
- [ ] Tablet (768x1024) - Modal fits screen
- [ ] Mobile (375x667) - All elements accessible

**Result:** ✅ PASS / ❌ FAIL

---

### 6.3 Loading States
**Test:** Loading indicators during operations

**Check:**
- [ ] "Adding..." shown during add
- [ ] Buttons disabled during operations
- [ ] No double-submissions possible
- [ ] Loading states clear and visible

**Result:** ✅ PASS / ❌ FAIL

---

### 6.4 Error Handling
**Test:** Error messages display correctly

**Check:**
- [ ] Errors show in red alert boxes
- [ ] Error messages clear and helpful
- [ ] Errors auto-dismiss after 3 seconds
- [ ] Multiple errors don't stack

**Result:** ✅ PASS / ❌ FAIL

---

## 7. Integration Tests

### 7.1 Journey Management → Dashboard
**Test:** Changes reflect on dashboard

**Steps:**
1. Add Traveler journey in Settings
2. Switch to Traveler
3. Navigate to Dashboard

**Expected:**
- [ ] Dashboard shows Traveler theme
- [ ] Hero section correct
- [ ] Sections appropriate for Traveler
- [ ] Colors match Traveler journey

**Result:** ✅ PASS / ❌ FAIL

---

### 7.2 Dashboard → Settings → Dashboard
**Test:** Round-trip journey switching

**Steps:**
1. Start on Dashboard (Student active)
2. Go to Settings
3. Switch to Professional
4. Return to Dashboard

**Expected:**
- [ ] Dashboard updates to Professional
- [ ] No page refresh needed
- [ ] Smooth transition
- [ ] All data loads correctly

**Result:** ✅ PASS / ❌ FAIL

---

### 7.3 Multiple Browser Tabs
**Test:** Journey changes sync across tabs

**Steps:**
1. Open Settings in Tab 1
2. Open Dashboard in Tab 2
3. Switch journey in Tab 1
4. Refresh Tab 2

**Expected:**
- [ ] Tab 2 shows updated active journey
- [ ] No conflicts or errors
- [ ] Data consistent across tabs

**Result:** ✅ PASS / ❌ FAIL

---

## 8. API Integration Tests

### 8.1 Add Journey API Call
**Test:** POST /api/v1/journeys/select

```bash
curl -X POST http://localhost:8000/api/v1/journeys/select \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"journey_type": "traveler", "level": "Beginner", "is_primary": false}'
```

**Expected:** 201 Created, journey object returned

**Result:** ✅ PASS / ❌ FAIL

---

### 8.2 Switch Journey API Call
**Test:** PUT /api/v1/journeys/switch

```bash
curl -X PUT http://localhost:8000/api/v1/journeys/switch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"journey_id": "journey_id_here"}'
```

**Expected:** 200 OK, updated journey list

**Result:** ✅ PASS / ❌ FAIL

---

### 8.3 Remove Journey API Call
**Test:** DELETE /api/v1/journeys/{id}

```bash
curl -X DELETE http://localhost:8000/api/v1/journeys/journey_id_here \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** 200 OK, journey removed

**Result:** ✅ PASS / ❌ FAIL

---

### 8.4 Get Journeys API Call
**Test:** GET /api/v1/journeys/my-journeys

```bash
curl http://localhost:8000/api/v1/journeys/my-journeys \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** 200 OK, list of user's journeys

**Result:** ✅ PASS / ❌ FAIL

---

## 9. Edge Cases

### 9.1 Network Error During Add
**Test:** Simulate network failure

**Expected:**
- [ ] Error message displayed
- [ ] Modal stays open
- [ ] Can retry operation
- [ ] No partial data saved

**Result:** ✅ PASS / ❌ FAIL

---

### 9.2 Concurrent Journey Operations
**Test:** Multiple operations simultaneously

**Expected:**
- [ ] Operations queued properly
- [ ] No race conditions
- [ ] Data consistency maintained

**Result:** ✅ PASS / ❌ FAIL

---

### 9.3 Invalid Journey Data
**Test:** Backend returns invalid data

**Expected:**
- [ ] Graceful error handling
- [ ] User-friendly error message
- [ ] App doesn't crash

**Result:** ✅ PASS / ❌ FAIL

---

## 10. Performance Tests

### 10.1 Modal Open Time
**Measure:** Time to open Add Journey modal

**Expected:** < 100ms

**Result:** ___ms - ✅ PASS / ❌ FAIL

---

### 10.2 Journey Switch Time
**Measure:** Time to switch active journey

**Expected:** < 500ms

**Result:** ___ms - ✅ PASS / ❌ FAIL

---

### 10.3 Journey Add Time
**Measure:** Time to add new journey (API call)

**Expected:** < 1000ms

**Result:** ___ms - ✅ PASS / ❌ FAIL

---

## Summary

### Test Statistics
- **Total Tests:** 40
- **Passed:** ___
- **Failed:** ___
- **Skipped:** ___
- **Pass Rate:** ___%

### Critical Issues
1. 
2. 
3. 

### Minor Issues
1. 
2. 
3. 

### Recommendations
1. 
2. 
3. 

### Next Steps
- [ ] Fix critical issues
- [ ] Address minor issues
- [ ] Proceed to Phase 6 (Content Filtering)
- [ ] Update documentation

---

## Manual Testing Instructions

1. **Login:** http://localhost:3000/login (saud@gmail.com / password)
2. **Navigate to Settings:** http://localhost:3000/settings
3. **Test Add Journey:**
   - Click "Add Journey"
   - Select each journey type
   - Select levels
   - Verify journeys added
4. **Test Switch Journey:**
   - Click "Switch" on different journeys
   - Verify active badge moves
   - Check dashboard updates
5. **Test Remove Journey:**
   - Click "Remove" on journeys
   - Verify confirmation dialog
   - Check last journey protection
6. **Test Progress Display:**
   - Verify stats accuracy
   - Check progress bars
7. **Test Responsive:**
   - Resize browser window
   - Test on mobile device
8. **Test Dark Mode:**
   - Toggle dark mode
   - Verify all elements visible

---

**Status:** ⏳ READY FOR TESTING
**Tester:** Manual testing required
**Environment:** Docker (Frontend + Backend)
