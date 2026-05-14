```markdown
# Design System Specification: The Kinetic Luminescence

## 1. Overview & Creative North Star
The Creative North Star for this design system is **"The Digital Laboratory."** 

This is not a generic SaaS dashboard; it is a high-precision instrument for elite creators. The aesthetic rejects the "flatness" of modern web design in favor of **Tonal Depth and Kinetic Light.** We move beyond standard layouts by using intentional asymmetry and "light-leak" accents that mimic the precision of a laser or a high-end camera sensor. The interface should feel as though it is powered by the machine learning algorithms it houses—intelligent, reactive, and sophisticated.

By leveraging deep charcoal foundations against vibrant, neon-gas accents, we create a "low-light" environment that reduces eye strain and allows the user’s creative work to become the brightest element on the screen.

---

## 2. Colors & Surface Architecture
The color palette is built on a foundation of "absolute depth" to ensure that the Cyan and Purple accents feel like light sources rather than mere pigments.

### Surface Hierarchy & Nesting
To create a premium feel, we abandon traditional borders. Hierarchy is achieved through **Surface Stacking**:
*   **Base Layer:** `surface` (#0e0e0e) – The infinite canvas.
*   **Secondary Sections:** `surface-container-low` (#131313) – For sidebars and secondary utility zones.
*   **Interactive Components:** `surface-container` (#1a1a1a) – For primary tool containers.
*   **Prominent Floating Elements:** `surface-container-highest` (#262626) – For modals or active tool palettes.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to define sections. Sectioning must be achieved through background color shifts. A `surface-container-low` panel sitting on a `surface` background provides all the definition a professional eye needs. 

### The "Glass & Gradient" Rule
To evoke a high-tech machine learning aesthetic, use **Glassmorphism** for floating HUDs (Heads-Up Displays). 
*   **Token:** Use `surface-variant` at 60% opacity with a `24px` backdrop blur.
*   **Signature Textures:** Main CTAs should utilize a linear gradient from `primary` (#81ecff) to `primary-container` (#00e3fd) at a 135-degree angle. This mimics the "glow" of a high-end hardware interface.

---

## 3. Typography
We utilize **Inter** exclusively to maintain a professional, Swiss-engineered clarity.

*   **Display (lg/md):** Reserved for high-impact editorial moments (e.g., "Generative Fill Complete"). Use `display-lg` with `-0.02em` letter spacing to feel "tight" and engineered.
*   **Headline (sm/md):** Used for tool category headers. These should feel authoritative.
*   **Title (sm):** The workhorse for panel headers. Always use `on-surface` for maximum legibility.
*   **Body (md):** Used for all primary descriptions. 
*   **Label (sm):** Used for micro-copy and tooltips. 

**Editorial Hierarchy:** Break the grid by pairing a `display-sm` headline with a significantly smaller `label-md` subtext. This extreme contrast in scale conveys a premium, "designed" feel rather than a templated one.

---

## 4. Elevation & Depth
In this system, elevation is a property of **Light and Opacity**, not structural shadows.

*   **The Layering Principle:** Depth is achieved by "stacking" container tiers. Place a `surface-container-highest` card on top of a `surface-container-low` workspace to create an immediate, natural lift.
*   **Ambient Shadows:** For floating elements, use an extra-diffused shadow: `box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);`. Never use pure black shadows; let the background color bleed into the shadow.
*   **The "Ghost Border" Fallback:** If a container requires further definition (e.g., an active input), use the `outline-variant` token at **20% opacity**. This creates a "subtle glowing border" effect that feels high-tech rather than restrictive.
*   **Neon Accents:** Use `secondary` (#e966ff) sparingly to highlight AI-driven features, creating a "signature" look that differentiates human-input tools from machine-assisted tools.

---

## 5. Components

### Buttons
*   **Primary:** Gradient of `primary` to `primary-container`. `8px` (xl) corner radius. No border.
*   **Secondary:** `surface-container-highest` background with a `primary` "Ghost Border" (20% opacity).
*   **Tertiary:** Ghost button using `primary` text. No background until hover (`surface-variant` at 30%).

### Input Fields
*   **Default:** `surface-container-low` background, no border, `8px` radius.
*   **Active State:** 1px "Ghost Border" using `primary`. Add a subtle outer glow: `0 0 8px rgba(129, 236, 255, 0.2)`.

### Cards & Tool Palettes
*   **Rule:** Forbid the use of divider lines. Separate content using `16px` or `24px` vertical white space from the spacing scale. 
*   **Active Selection:** An active card should not have a thick border; instead, use a `2px` left-side accent bar in `secondary` (#e966ff).

### Signature Component: The "AI Pulse"
*   For components involving machine learning (like an image processing state), use a `primary-dim` to `secondary-dim` soft radial gradient background that pulses slowly (2s ease-in-out), suggesting "thought" or "calculation."

---

## 6. Do's and Don'ts

### Do
*   **Do** use extreme whitespace to group elements.
*   **Do** use `secondary` (Purple) to denote "Intelligence" or "Magic" features.
*   **Do** use `primary` (Cyan) for "Utility" and "Action" features.
*   **Do** ensure all "Glass" elements have a `backdrop-filter: blur()`.

### Don't
*   **Don't** use 100% opaque, high-contrast borders (e.g., pure white or bright cyan).
*   **Don't** use standard "drop shadows" (small blur, high opacity).
*   **Don't** use dividers between list items; let the `surface-container` shifts do the work.
*   **Don't** use sharp 90-degree corners; always stick to the `8px` (xl) or `full` roundedness scale.

---

## 7. Interaction Patterns
Transitions between states should be **snappy yet fluid**. Use a `200ms cubic-bezier(0.4, 0, 0.2, 1)` for all hover states. When a user hovers over a primary tool, the "Ghost Border" should subtly increase in brightness, mimicking the warm-up of a high-tech filament.```