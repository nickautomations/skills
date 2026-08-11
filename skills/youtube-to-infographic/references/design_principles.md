# Nick Automations Infographic — Design System Reference

This is the full design system spec. The SKILL.md gives high-level guidance; this file is what you consult when actually writing the HTML/CSS to make sure the output is on-brand at the pixel level.

## Color tokens (exact hex codes — no substitutions)

```css
:root {
  --na-orange:      #FF6B35;  /* primary accent — slashes, command tags, key highlights */
  --na-orange-soft: #FFE8DA;  /* very pale orange — backgrounds for command badges */
  --na-ink:         #1A1A1A;  /* near-black — headings, logo, illustrations */
  --na-body:        #3F3F50;  /* dark slate — body text */
  --na-muted:       #8A8578;  /* warm gray — metadata, labels */
  --na-cream:       #FAF7F2;  /* warm cream — page background */
  --na-card:        #FFFFFF;  /* pure white — card surfaces */
  --na-subtle:      #F5EFE8;  /* peach-cream — secondary card fills */
  --na-divider:     #E8E4DD;  /* warm gray — horizontal rules, borders */
}
```

**Usage proportions** (60-30-10 rule, modified):
- 65% cream/white surfaces (`--na-cream` + `--na-card`)
- 25% dark text (`--na-ink` + `--na-body`)
- 5% orange (`--na-orange`)
- 5% supporting (muted gray, soft orange, dividers)

## Typography scale

Load via Fontshare (Satoshi) + Google Fonts (Geist, Cabinet Grotesk, JetBrains Mono):

```html
<link rel="preconnect" href="https://api.fontshare.com">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;700;800;900&family=Cabinet+Grotesk:wght@500;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

**Inter is banned** in this design system per the design-taste check. Use `'Satoshi', 'Geist', 'Cabinet Grotesk', system-ui, sans-serif` exclusively.

**Monospace stack** — for command names, file paths, badges, and category labels:
`'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace`. Every command like `/clear`,
every file like `SKILL.md`, every label like `BREAKDOWN / [topic]` gets the mono treatment.
It signals "this is a real, technical thing." The `SF Mono`/`Menlo`/`Consolas` tiers keep
macOS and Windows from dropping to a generic monospace when JetBrains Mono is slow to load.

**Why this cascade**: Satoshi has the strongest editorial character (slightly humanist
proportions, premium feel). Geist is Vercel's geometric sans and falls back cleanly when
Fontshare is slow. Cabinet Grotesk is another high-end editorial sans as a third tier.
System UI catches everything else without visible degradation. The tight tracking
(`-0.03em` on display sizes) works across all three because they are geometric sans serifs
with similar x-heights — a fallback swap won't visibly jolt the layout.

Full type scale:

```css
/* Base */
body {
  font-family: 'Satoshi', 'Geist', 'Cabinet Grotesk', system-ui, -apple-system, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: var(--na-body);
}

/* Mega headline (hero) */
.headline-xl {
  font-size: clamp(48px, 7vw, 88px);
  font-weight: 900;
  line-height: 0.98;
  letter-spacing: -0.035em;
  color: var(--na-ink);
}

/* Column header */
.column-title {
  font-size: 22px;
  font-weight: 800;
  line-height: 1.15;
  color: var(--na-ink);
  letter-spacing: -0.01em;
}

/* Card title */
.card-title {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.015em;
  color: var(--na-ink);
}

/* Body text */
.body-text {
  font-size: 14.5px;
  font-weight: 400;
  line-height: 1.55;
  color: var(--na-body);
}

/* Lede subtitle */
.lede {
  font-size: 16px;
  font-weight: 400;
  line-height: 1.55;
  color: var(--na-body);
}

/* Metadata labels (all caps, mono) */
.meta-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--na-muted);
}

/* Command badge (the /clear, /review style tags) */
.command-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 500;
  color: var(--na-ink);
  background: var(--na-card);
  border: 1px solid var(--na-divider);
  border-radius: 6px;
  padding: 4px 10px;
  display: inline-block;
}

/* Item number (01, 02...) */
.item-number {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 500;
  color: var(--na-muted);
  letter-spacing: 0.05em;
}

/* The slash treatment */
.brand-slash {
  color: var(--na-orange);
  font-weight: 900;
  font-style: normal;
  margin: 0 0.02em;
}
```

## Layout grid

Page width: `max-width: 1080px` (optimal for social), centered.

Three-column grid for the main content:

```css
.columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  padding: 0 48px 48px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

@media (max-width: 768px) {
  .columns { grid-template-columns: 1fr; }
}
```

Vertical rhythm: use 8px as the base unit. Common spacings: 16, 24, 32, 48, 64, 96.

## Alignment discipline (CRITICAL — read before writing card HTML)

The single most common quality issue with this design is **cards in different columns ending at different heights**, which breaks the editorial-grid feel. The fix is structural, not aesthetic — every card must reserve the same vertical space for each region. Follow these rules without exception.

### Rule 1: Use the row-aligned card layout

Every card is a flexbox column with reserved minimum heights for each region. The footer is pinned to the bottom using `margin-top: auto` so cards always end at the same vertical position across the row, even when bodies are different lengths.

```css
/* The column itself uses fixed gap, NOT auto-sized */
.column {
  display: flex;
  flex-direction: column;
  gap: 36px;
}

/* Each card is a flex column with the footer pinned to the bottom */
.card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1 1 auto;        /* allow cards to expand to match row */
  min-height: 0;
}

/* The illustration is a FIXED height — not min-height, not max-height. Fixed. */
.card-illustration {
  background: var(--na-card);
  border: 1px solid var(--na-divider);
  border-radius: 10px;
  padding: 16px;
  height: 160px;          /* HARD LOCK — every illustration is 160px tall */
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-illustration svg {
  max-width: 100%;
  max-height: 128px;      /* SVG content fits inside the 160px box with padding */
  height: auto;
}

/* Card title gets a min-height equivalent to two lines, so 1-line and 2-line
   titles both reserve the same space and bodies start at the same Y position */
.card-title {
  font-size: 21px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.015em;
  color: var(--na-ink);
  min-height: calc(21px * 1.2 * 2);  /* exactly two lines */
}

/* Body gets a min-height equivalent to 3 lines so short bodies don't
   cause the footer to creep up */
.body-text {
  font-size: 14px;
  line-height: 1.55;
  color: var(--na-body);
  min-height: calc(14px * 1.55 * 3); /* exactly three lines */
}

/* Footer pins to bottom of card */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--na-divider);
  margin-top: auto;       /* THIS is what pins the footer */
}
```

### Rule 2: Pin column heights to the row

The `.columns` grid container needs `align-items: stretch` (the default — just don't override it) so all three columns stretch to the height of the tallest. Cards inside each column then distribute using `flex: 1 1 auto` on `.card`.

But there's a catch: if column A has 2 cards and column B has 3 cards, column A's cards will stretch into the extra space. For a column grid, either:

- **Preferred for grids**: ensure all columns have the same number of cards (2 each → 6 total, 3 each → 9 total)
- **Better alternative**: if the source does not naturally balance into equal columns, switch to a timeline, checklist, comparison split, compact brief, or hero + evidence layout instead of forcing filler cards
- **Fallback inside custom layouts**: add `flex: 0 0 auto` to `.card` to disable stretching, accept that sections may end at different heights but rows will still line up

### Rule 3: Constrain body copy length

The most reliable way to keep cards aligned is to keep the *content* uniform. Enforce these limits in every card:

| Region | Limit | Why |
|--------|-------|-----|
| Command badge | 1-3 words, no spaces if possible | Single-line fit |
| Card title | 4-8 words, fits in 2 lines max | Avoid 3-line wraps |
| Card body | 25-50 words, 2-3 sentences | Fits 3 lines reliably |

If a point can't be expressed in 50 words, split it into two cards. If a title needs three lines, shorten it. This is the brand discipline.

### Rule 4: Choose the right layout before forcing columns

For visual coherence, **every column grid should have the same number of cards**. Common configurations:

- 2 cards × 3 columns = 6 cards total (recommended for most pieces)
- 3 cards × 3 columns = 9 cards total (use for comprehensive "X features" pieces)
- 4 cards × 3 columns = 12 cards total (only for very dense content; consider splitting into two pieces)

Asymmetric column grids (2-3-2) break the editorial grid and look like an accident. If a source does not naturally support equal columns, do not pad it into 6 or 9 cards. Use a different layout shape:

- **Compact brief**: 1 hero insight + 3-5 supporting cards
- **Timeline/process map**: 5-7 ordered steps
- **Checklist/playbook**: 4-8 tactical checks in one or two columns
- **Comparison split**: two opposing sides + a takeaway band
- **Hero + evidence**: one large thesis, 3-6 proof points, and a CTA

### Rule 5: Visual verification before delivering

After generating the HTML, mentally trace these alignment checks:

- ✅ All three columns end at the same vertical position
- ✅ All card illustrations are the same height
- ✅ All card titles occupy the same number of lines (or have reserved space for the longest)
- ✅ All card bottoms sit at the same Y position within their row

If any of these would fail, fix the content (shorten titles, split cards) or the CSS (verify the min-heights and `margin-top: auto` are in place).

## Striped header (the diagonal pattern at the top)

```css
.brand-stripes {
  height: 18px;
  background: repeating-linear-gradient(
    -45deg,
    var(--na-orange) 0 6px,
    transparent 6px 12px
  );
}
```

Place this as the very first element above the page header. It's a strong visual anchor and a recognizable brand signature for Nick Automations infographics.

## Page header (category label + logo)

```html
<div class="page-header">
  <div class="meta-left">
    <div class="meta-label accent">BREAKDOWN / [TOPIC]</div>
  </div>
  <div class="brand-mark">
    <!-- inline SVG logo here -->
    <span class="wordmark">Nick<span class="brand-slash">/</span>AUTOMATIONS</span>
  </div>
</div>
```

The top-left label is **contextual** — pick from `BREAKDOWN`, `PLAYBOOK`, `TOOLKIT`, `BRIEFING`, `GUIDE`, `COMPARED`, `TAKE` based on what the content actually is. Always followed by ` / [TOPIC]` in the same mono caps style. The whole label gets `color: var(--na-orange)` via the `accent` class to anchor the page visually.

```css
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 48px 24px;
  border-bottom: 1px solid var(--na-divider);
}

.brand-mark {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-mark svg { width: 28px; height: 28px; }

.wordmark {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 700;
  color: var(--na-ink);
  letter-spacing: 0.04em;
}
```

## Hero section

```html
<section class="hero">
  <h1 class="headline-xl">
    Master Claude.<br>
    9 features<span class="brand-slash">/</span>that<br>
    actually exist.
  </h1>
  <p class="lede">[2-3 sentence intro paragraph]</p>
</section>
```

```css
.hero {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 48px;
  padding: 56px 48px 48px;
  align-items: end;
}

.hero .lede {
  align-self: end;
  max-width: 320px;
}
```

Headline on the left, lede on the right, both bottom-aligned. This editorial split is part of the look.

## Column header

```html
<div class="column-header">
  <div class="column-icon"><!-- inline SVG --></div>
  <div class="meta-label">COLUMN 01 / 03</div>
  <h2 class="column-title">SESSION<br>DISCIPLINE</h2>
</div>
```

```css
.column-header {
  padding-bottom: 16px;
  border-bottom: 1px solid var(--na-divider);
  margin-bottom: 8px;
}

.column-icon {
  width: 44px;
  height: 44px;
  background: var(--na-subtle);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.column-icon svg {
  width: 24px;
  height: 24px;
  stroke: var(--na-ink);
  fill: none;
  stroke-width: 1.75;
}

.column-title { margin: 8px 0 0; }
```

Column titles in ALL CAPS, two-line break (e.g., "SESSION / DISCIPLINE", "QUALITY / GATES", "EXTEND / CLAUDE").

## Card

```html
<article class="card">
  <div class="card-top">
    <span class="item-number">01</span>
    <span class="command-badge">/clear</span>
  </div>
  <div class="card-illustration">
    <!-- inline SVG, ~280×140 -->
  </div>
  <h3 class="card-title">Start fresh,<span class="brand-slash">/</span>not fight drift.</h3>
  <p class="body-text">[2-3 sentence body]</p>
</article>
```

Note: **no source tags, no card-footer**. Cards end cleanly at the body. The brand's CTA appears once at the page footer, not on every card.

```css
.card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1 1 auto;
  min-height: 0;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* HARD-LOCKED illustration height — see Alignment Discipline section */
.card-illustration {
  background: var(--na-card);
  border: 1px solid var(--na-divider);
  border-radius: 10px;
  padding: 16px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-illustration svg {
  max-width: 100%;
  max-height: 128px;
  height: auto;
}

/* min-height reserves 2 lines so 1-line titles don't shift body up */
.card-title {
  font-size: 21px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.015em;
  color: var(--na-ink);
  min-height: calc(21px * 1.2 * 2);
}

/* min-height reserves 3 lines so short bodies don't pull footer up */
.body-text {
  font-size: 14px;
  line-height: 1.55;
  color: var(--na-body);
  min-height: calc(14px * 1.55 * 3);
}
```

Cards have no internal footer — they end at the body text. Alignment across columns is still maintained by the `min-height` rules on `.card-title` and `.body-text`, plus `flex: 1 1 auto` on `.card`, which together pin all cards in a row to the same height.

## Reference table (page 2)

For long lists that don't fit the main grid:

```css
.reference-table {
  background: var(--na-card);
  border-radius: 12px;
  padding: 32px;
}

.reference-table .label {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: var(--na-ink);
  font-size: 14px;
}

.reference-table .row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 24px;
  padding: 14px 0;
  border-bottom: 1px solid var(--na-divider);
}

.reference-table .row:last-child { border-bottom: none; }
```

## Footer (soft CTA — always include)

The footer is a single line: a soft call-to-action driving to nickautomations.com. No source list, no volume label, no other text. The CTA is the only thing at the bottom.

```html
<footer class="page-footer">
  <div class="footer-cta">
    See how we automate<span class="brand-slash">/</span><span class="cta-link">nickautomations.com</span>
  </div>
</footer>
```

```css
.page-footer {
  padding: 32px 48px 40px;
  border-top: 1px solid var(--na-divider);
  margin-top: 48px;
  display: flex;
  justify-content: center;
}

.footer-cta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12.5px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--na-ink);
}

.footer-cta .cta-link {
  color: var(--na-orange);
  font-weight: 700;
}
```

The "See how we automate" half is in `--na-ink` (dark), the URL "nickautomations.com" is in `--na-orange`, and the slash between them is the brand orange-slash treatment. The whole line is centered, small, mono caps. Restrained — never the loudest thing on the page.

## Common mistakes to avoid

1. **Don't introduce off-palette colors.** Stick to the tokens. No teal, no yellow accents, no gradients.
2. **Don't use the slash as decoration.** It's a content separator inside phrases. Don't sprinkle slashes randomly.
3. **Don't use serif fonts.** Satoshi / Geist / Cabinet Grotesk + JetBrains Mono only. The design's strength comes from typographic discipline.
4. **Don't pack cards with too much text.** 2-3 sentences. If a point needs more, it's two points.
5. **Don't add source tags to cards.** Cards end clean at the body. The brand owns the piece; viewers don't need attribution receipts on every card.
6. **Don't AI-generate illustrations.** Hand-code SVG using the snippets in `illustrations.md`.
7. **Don't forget the diagonal stripe at the top.** It's the brand signature.
8. **Don't use external image links** — embed all SVGs inline so the file is fully portable.
9. **Don't replace or extend the footer.** It's exactly one line: the CTA. No source lists. No volume labels.

## When in doubt

The Nick Automations infographic aesthetic is what you'd get if *The Economist* designed a developer documentation page. Editorial restraint, typographic confidence, one strong accent color. When choosing between two options, pick the more restrained one.
