### Root Cause Analysis

On your website, there are currently **two types of download mechanisms**:

1. **Direct PDF Downloads (Working properly):**
   * On [dokumente.html](file:///c:/Users/super/Desktop/Hk%20Energieberatung/dokumente.html) under *"Offizielle Merkblätter & Vorlagen"*, there are **7 ready official PDF files** located in [assets/dokumente/](file:///c:/Users/super/Desktop/Hk%20Energieberatung/assets/dokumente). Clicking them triggers a direct 1-click file download.

2. **Lead-Magnet Email Forms (The issue):**
   * On [dokumente.html](file:///c:/Users/super/Desktop/Hk%20Energieberatung/dokumente.html) (*"Exklusive Experten-Downloads"*), [expressausweis.html](file:///c:/Users/super/Desktop/Hk%20Energieberatung/expressausweis.html) (*"GEG-Entscheider"*), and the Exit-Intent Popup on [index.html](file:///c:/Users/super/Desktop/Hk%20Energieberatung/index.html) (*"Förderkompass 2026"*), there are email capture forms sending requests to [forms/contact.php](file:///c:/Users/super/Desktop/Hk%20Energieberatung/forms/contact.php).
   * **Why it redirects/fails:** [contact.php](file:///c:/Users/super/Desktop/Hk%20Energieberatung/forms/contact.php) is programmed as a complete contact form expecting `Name`, `Message`, and `Privacy Policy` consent. Because these download cards only ask for an email, the backend rejects it with an error or redirects to the raw PHP URL, and the advertised PDFs haven't been created yet.

---

### 3 Solutions You Can Choose From

#### Option 1: Replace with Direct CTAs / Existing Documents *(Recommended & Fast)*
* **Exit-Intent Popup on [index.html](file:///c:/Users/super/Desktop/Hk%20Energieberatung/index.html):** Instead of offering an unmade PDF, change the popup into a call-to-action for a **"Free Initial Consultation"** or **"Energy Certificate Express Check"** (linking directly to the form/contact section).
* **GEG-Entscheider on [expressausweis.html](file:///c:/Users/super/Desktop/Hk%20Energieberatung/expressausweis.html):** Replace the email form with a direct button: *"Determine your certificate type in 2 minutes"* (smooth-scrolls right down to the interactive form).
* **Lead Magnet cards on [dokumente.html](file:///c:/Users/super/Desktop/Hk%20Energieberatung/dokumente.html):** Either temporarily remove/hide this section or link the cards directly to the 7 existing PDFs in [assets/dokumente/](file:///c:/Users/super/Desktop/Hk%20Energieberatung/assets/dokumente).

---

#### Option 2: Generate the 3 Missing PDF Documents for You
* We can generate 3 clean, branded, professional PDF guides and put them into [assets/dokumente/](file:///c:/Users/super/Desktop/Hk%20Energieberatung/assets/dokumente):
  1. **Sanierungs- & Förderkompass 2026** (Guide on BEG/KfW funding rates, 5% iSFP bonus, and requirements).
  2. **GEG-Entscheider Leitfaden** (Decision matrix: When is a Verbrauchsausweis sufficient vs. when is a Bedarfsausweis mandatory under GEG?).
  3. **Vorbereitungs-Checkliste Erstberatung** (Checklist of documents property owners need before a consultation).
* The buttons will then be set up as immediate 1-click downloads with no redirection.

---

#### Option 3: Fix the Email Lead-Capture Backend
* If you want to collect leads' email addresses:
  * We update [contact.php](file:///c:/Users/super/Desktop/Hk%20Energieberatung/forms/contact.php) to accept email-only lead magnet submissions without validation errors.
  * The form will show a confirmation message (*"Thank you! We will email you the guide shortly."*) without redirecting or breaking.

---

### Which option would you like to proceed with?
Let me know if you'd like **Option 1** (streamlined CTAs & existing files), **Option 2** (create the 3 PDF guides), or **Option 3** (fix the email capture handler).