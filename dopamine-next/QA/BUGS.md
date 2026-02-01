# Bug Tracker - dopamine.watch Next.js

**Last Updated:** January 31, 2026

---

## Critical Bugs

### BUG-001: Profile Page Uses Hardcoded Mock Data
**Severity:** Critical
**Location:** `src/app/(app)/profile/page.tsx:29-51`
**Description:** Profile page displays hardcoded mock user data instead of fetching from auth context.
**Expected:** Should use `useAuth()` to get real user data
**Code:**
```tsx
// Current (broken)
const mockUser = {
  id: '1',
  name: 'Johan',
  email: 'johan@dopamine.watch',
  ...
}
const [user] = useState(mockUser)

// Should be
const { user, isPremium } = useAuth()
```
**Fix Required:** Replace mock data with auth context
**Status:** OPEN

---

### BUG-002: Sign Out Button Not Connected
**Severity:** Critical
**Location:** `src/app/(app)/profile/page.tsx:251-258`
**Description:** Sign out button has no onClick handler connected to auth context.
**Expected:** Should call `signOut()` from auth context
**Code:**
```tsx
// Current (broken)
<Button
  variant="ghost"
  className="w-full text-red-500..."
  icon={<SignOut size={20} />}
>
  Sign Out
</Button>

// Should have onClick
onClick={async () => {
  await signOut()
  router.push('/login')
}}
```
**Status:** OPEN

---

### BUG-003: No OpenAI Integration
**Severity:** Critical
**Location:** `src/app/(app)/chat/page.tsx:112-118`, `src/components/features/MrDpFloating.tsx`
**Description:** Mr.DP chat returns random mock responses instead of calling OpenAI API.
**Expected:** Should integrate with OpenAI for actual AI responses
**Status:** OPEN

---

## High Severity Bugs

### BUG-004: MoodSelector Target Icon Shows Placeholder
**Severity:** High
**Location:** `src/components/features/MoodSelector.tsx:371-379`
**Description:** Target mood icons display hardcoded "●" character instead of actual Phosphor icons.
**Code:**
```tsx
// Current (broken)
<span className="text-2xl" style={{ color: target.color }}>
  {/* Icon placeholder - we'd use Phosphor icons here */}
  ●
</span>
```
**Fix Required:** Import and use actual icons from moods.ts
**Status:** OPEN

---

### BUG-005: Missing Relative Positioning on Target Mood Card
**Severity:** High
**Location:** `src/components/features/MoodSelector.tsx:353-392`
**Description:** The checkmark icon uses `absolute` positioning but parent button lacks `relative`.
**Code:**
```tsx
// Button at line 353 is missing className="relative"
<motion.button
  className={cn(
    'p-6 rounded-2xl',
    // Missing: 'relative'
    ...
  )}
>
  ...
  {isSelected && (
    <motion.div
      className="absolute top-2 right-2..."  // This will position wrong!
    >
```
**Fix Required:** Add `relative` class to parent button
**Status:** OPEN

---

### BUG-006: isMobile() Causes Hydration Mismatch
**Severity:** High
**Location:** `src/components/features/MoodSelector.tsx:119-131`
**Description:** `isMobile()` checks `window.innerWidth` which returns false on server, causing different renders between SSR and client.
**Code:**
```tsx
{isMobile() ? (
  <MoodCarousel ... />
) : (
  <MoodGrid ... />
)}
```
**Fix Required:** Use CSS media queries or useEffect-based detection
**Status:** OPEN

---

### BUG-007: No Stripe Payment Integration
**Severity:** High
**Location:** Entire app
**Description:** No Stripe keys in `.env.local`, no payment links, no checkout flow.
**Expected:** Should have Stripe integration for premium subscriptions
**Status:** OPEN

---

## Medium Severity Bugs

### BUG-008: All Pages Use Mock Data
**Severity:** Medium
**Location:** Multiple files
**Affected:**
- `src/app/(app)/home/page.tsx` - continueWatching, forYou arrays
- `src/app/(app)/quick-hit/page.tsx` - featuredContent array
- `src/app/(app)/recommendations/page.tsx` - mockContent array
**Description:** No real TMDB API calls, all content is hardcoded.
**Status:** OPEN

---

### BUG-009: Images Not Optimized
**Severity:** Medium
**Location:** Multiple files
**Description:** Using `<img>` tags with raw TMDB URLs instead of Next.js `<Image>` component.
**Affected Files:**
- `src/app/(app)/home/page.tsx:333, 386`
- `src/app/(app)/quick-hit/page.tsx:232`
- `src/app/(app)/recommendations/page.tsx:358`
**Fix Required:** Replace with next/image for optimization
**Status:** OPEN

---

### BUG-010: Missing SEO Metadata
**Severity:** Medium
**Location:** `src/app/layout.tsx`
**Description:** No page-specific metadata, titles, or descriptions.
**Fix Required:** Add metadata export to each page
**Status:** OPEN

---

### BUG-011: Missing Error Boundaries
**Severity:** Medium
**Location:** Entire app
**Description:** No React error boundaries to catch and display errors gracefully.
**Fix Required:** Add error.tsx files to route segments
**Status:** OPEN

---

## Low Severity Bugs

### BUG-012: Accessibility - Missing aria-labels
**Severity:** Low
**Location:** Multiple files
**Affected Elements:**
- Icon-only buttons in Navigation
- Heart/Plus buttons on content cards
- Mood carousel navigation dots
**Fix Required:** Add aria-label attributes
**Status:** OPEN

---

### BUG-013: Navigation Shows Same Items for All Users
**Severity:** Low
**Location:** `src/components/layout/Navigation.tsx`
**Description:** Navigation doesn't change based on auth state (logged in vs logged out).
**Expected:** Should show Login button when not authenticated
**Status:** OPEN

---

### BUG-014: Color Contrast Issues
**Severity:** Low
**Location:** Multiple
**Description:** Some text colors may not meet WCAG contrast requirements:
- Surface-400 text on white background
- White/70 text on gradients
**Fix Required:** Audit and adjust colors
**Status:** OPEN

---

### BUG-015: Missing Focus States
**Severity:** Low
**Location:** Multiple buttons
**Description:** Some custom buttons lack visible focus indicators for keyboard navigation.
**Status:** OPEN

---

## Enhancement Requests

### ENH-001: Add Dark Mode Toggle
**Location:** Profile page settings
**Description:** Dark mode switch exists in UI but has no functionality.
**Status:** REQUESTED

---

### ENH-002: Add Loading Skeletons to All Pages
**Location:** Multiple pages
**Description:** Some pages lack proper loading states during data fetching.
**Status:** REQUESTED

---

### ENH-003: Add Offline Support
**Description:** PWA should work offline with cached content.
**Status:** REQUESTED

---

## Bug Statistics

| Severity | Count | Fixed | Open |
|----------|-------|-------|------|
| Critical | 3 | 0 | 3 |
| High | 4 | 0 | 4 |
| Medium | 4 | 0 | 4 |
| Low | 4 | 0 | 4 |
| **Total** | **15** | **0** | **15** |

---

## Changelog

- **2026-01-31:** Initial bug report created
