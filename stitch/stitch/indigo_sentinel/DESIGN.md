# Design System Specification: The Fluid Authority

## 1. Overview & Creative North Star
### Creative North Star: "The Digital Curator"
This design system moves beyond the rigid, boxy constraints of traditional enterprise software. Our goal is to create an environment that feels like a high-end editorial gallery—secure, authoritative, yet effortlessly fluid. We achieve this through "The Digital Curator" philosophy: every element is curated for maximum clarity, using breathable layouts and sophisticated tonal layering to guide the user without the noise of traditional UI "clutter."

By leveraging **Material You** logic with a custom editorial twist, we replace mechanical grids with intentional asymmetry and overlapping surfaces. The result is a premium, enterprise-grade experience that feels "fast" not just through performance, but through visual lightness.

---

## 2. Colors & Surface Logic
The palette is rooted in the depth of `Deep Indigo` and the vitality of `Energetic Teal`, balanced by a sophisticated range of neutral "Surfaces."

### The "No-Line" Rule
**Explicit Instruction:** Solid 1px borders are prohibited for sectioning. Structural definition must be achieved through background shifts or tonal transitions. Use `surface_container_low` vs. `surface` to define boundaries.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of semi-translucent materials.
*   **Base Level:** `surface` (#fbf8ff) – Used for the primary application background.
*   **Layer 1 (The Canvas):** `surface_container_low` (#f4f2fc) – Use for large sidebar containers or background sections.
*   **Layer 2 (The Focus):** `surface_container_lowest` (#ffffff) – Use for primary content cards or data tables to make them "pop" against the canvas.
*   **The "Glass & Gradient" Signature:** For high-impact areas (Hero sections, Profile summaries), use a linear gradient from `primary` (#24389c) to `primary_container` (#3f51b5) at a 135-degree angle.

### Signature Glassmorphism
Floating elements (Modals, Popovers, Floating Action Buttons) must use:
*   **Fill:** `surface_container_low` at 70% opacity.
*   **Effect:** Backdrop Blur (20px to 32px).
*   **Edge:** A "Ghost Border" using `outline_variant` (#c5c5d4) at 15% opacity to catch the light.

---

## 3. Typography
We use a dual-typeface system to balance character with readability. **Manrope** provides a modern, geometric authority for headers, while **Inter** ensures high-performance legibility for data.

*   **Display (Manrope):** Large, expressive scales (`display-lg`: 3.5rem) used for dashboard welcomes or high-level metrics.
*   **Headline (Manrope):** Professional and sturdy. Use `headline-sm` (1.5rem) for section headers to establish immediate hierarchy.
*   **Body (Inter):** The workhorse. `body-md` (0.875rem) is the default for all enterprise data entry and descriptions.
*   **Labels (Inter):** Used for micro-copy and metadata. Always uppercase with +5% letter spacing to maintain a premium feel.

---

## 4. Elevation & Depth
Depth is not a "drop shadow"—it is a spatial relationship.

*   **Tonal Layering:** To lift a card, do not reach for a shadow first. Instead, place a `surface_container_lowest` (#ffffff) element on top of a `surface_container` (#efedf6) background.
*   **Ambient Shadows:** If a floating state is required (e.g., a dragged item), use:
    *   `Box-shadow: 0 12px 32px -4px rgba(26, 27, 34, 0.06);`
    *   The shadow color is derived from `on_surface` to keep it natural and integrated.
*   **The Layering Principle:** Nested components should move from "Darker/Duller" backgrounds to "Brighter/Whiter" backgrounds as they increase in importance or proximity to the user.

---

## 5. Components

### Buttons
*   **Primary:** Solid `primary` (#24389c) with `on_primary` (#ffffff) text. Corner radius: `lg` (1rem).
*   **Secondary:** `secondary_container` (#85f6e5) with `on_secondary_container` (#007166) text. No border.
*   **Tertiary:** Ghost style. No background; text uses `primary`. High-contrast interaction state uses a subtle `surface_container_high` fill on hover.

### Input Fields
*   **Style:** Minimalist. No bottom line or full box. Use a subtle `surface_container_high` fill with a `md` (0.75rem) corner radius.
*   **Focus State:** Transition the background to `surface_container_lowest` and add a 2px `primary` ghost-border (20% opacity).

### Cards & Lists
*   **Forbid Dividers:** Never use horizontal lines to separate list items. Use 16px of vertical whitespace or alternating tonal shifts (Zebra striping using `surface` and `surface_container_low`).
*   **The "Attendance Strip":** A custom component for this system—a slim vertical bar of `secondary` (#006a60) on the left edge of a card to denote "Active" or "Verified" status.

### Progress Indicators
*   Avoid standard circular loaders. Use a sleek, indeterminate linear track using a gradient of `secondary` to `primary` for a "fast" and "modern" feel.

---

## 6. Do's and Don'ts

### Do
*   **Do** use `xl` (1.5rem) rounded corners for main containers to evoke a friendly, modern tech aesthetic.
*   **Do** embrace asymmetrical white space. Let a header breathe with more space above than below it to create an "editorial" flow.
*   **Do** use `tertiary` (#6c3400) sparingly as an accent for "Attention Required" states—it provides a sophisticated alternative to standard "Warning Orange."

### Don't
*   **Don't** use pure black (#000000) for text. Use `on_surface` (#1a1b22) to maintain visual softness.
*   **Don't** stack more than three levels of surface nesting. If you need a fourth level, use a "Ghost Border."
*   **Don't** use standard Material Design 4px corners. This system requires the "Premium Roundness" of 12px–16px (`md` to `xl`) to feel modern and approachable.