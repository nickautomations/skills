# Illustration Library

Ready-to-use SVG illustrations for common concepts. All use the brand palette (`#1A1A1A` for ink, `#FF6B35` for accent, `#FFE8DA` for soft orange fill). Copy these directly into card `.card-illustration` containers.

## Design rules for all illustrations

- Stroke width: 1.75 to 2.5px
- Stroke linecap: round
- Stroke linejoin: round
- Only two colors: ink (#1A1A1A) and orange (#FF6B35); optionally soft orange fill (#FFE8DA)
- Flat, no shadows, no gradients
- Aim for "technical schematic" feel, not cartoon
- Size: viewBox `0 0 280 140`, the container will size them

## Reusable: Document / file

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <rect x="100" y="30" width="80" height="100" rx="4" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <path d="M160 30 L180 50 L160 50 Z" fill="#1A1A1A"/>
  <line x1="115" y1="60" x2="160" y2="60" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
  <line x1="115" y1="75" x2="170" y2="75" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
  <line x1="115" y1="90" x2="155" y2="90" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
  <line x1="115" y1="105" x2="170" y2="105" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
</svg>
```

## /clear — Document with slash + arrow forward

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <!-- old document with slash -->
  <rect x="40" y="40" width="70" height="80" rx="4" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="52" y1="60" x2="98" y2="60" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="52" y1="72" x2="98" y2="72" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="52" y1="84" x2="90" y2="84" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="35" y1="115" x2="115" y2="35" stroke="#FF6B35" stroke-width="4" stroke-linecap="round"/>
  <!-- arrow -->
  <line x1="135" y1="80" x2="180" y2="80" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
  <polyline points="170,72 180,80 170,88" fill="none" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- new clean document -->
  <rect x="195" y="40" width="50" height="80" rx="4" fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2"/>
</svg>
```

## /review — Code with diff lines + magnifier

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <rect x="30" y="25" width="170" height="90" rx="6" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <!-- traffic lights -->
  <circle cx="42" cy="38" r="3" fill="#1A1A1A"/>
  <circle cx="52" cy="38" r="3" fill="#1A1A1A"/>
  <circle cx="62" cy="38" r="3" fill="#1A1A1A"/>
  <!-- code lines -->
  <text x="42" y="62" font-family="JetBrains Mono, monospace" font-size="9" fill="#FF6B35" font-weight="700">+</text>
  <line x1="52" y1="60" x2="180" y2="60" stroke="#1A1A1A" stroke-width="1.25" opacity="0.5"/>
  <text x="42" y="78" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A" font-weight="700">-</text>
  <line x1="52" y1="76" x2="170" y2="76" stroke="#1A1A1A" stroke-width="1.25" opacity="0.5"/>
  <text x="42" y="94" font-family="JetBrains Mono, monospace" font-size="9" fill="#FF6B35" font-weight="700">!</text>
  <line x1="52" y1="92" x2="160" y2="92" stroke="#FF6B35" stroke-width="1.5"/>
  <text x="42" y="110" font-family="JetBrains Mono, monospace" font-size="9" fill="#FF6B35" font-weight="700">+</text>
  <line x1="52" y1="108" x2="175" y2="108" stroke="#1A1A1A" stroke-width="1.25" opacity="0.5"/>
  <!-- magnifier -->
  <circle cx="215" cy="80" r="22" fill="none" stroke="#1A1A1A" stroke-width="2.5"/>
  <line x1="231" y1="96" x2="248" y2="113" stroke="#1A1A1A" stroke-width="3" stroke-linecap="round"/>
</svg>
```

## SKILL.md — Three file folders

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <!-- file 1 -->
  <rect x="30" y="40" width="70" height="80" rx="4" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="30" y="40" width="70" height="14" fill="#FF6B35" rx="4"/>
  <text x="38" y="74" font-family="JetBrains Mono, monospace" font-size="8" fill="#1A1A1A" font-weight="700">SKILL.md</text>
  <text x="38" y="110" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A">pdf/</text>
  <!-- file 2 -->
  <rect x="110" y="40" width="70" height="80" rx="4" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="110" y="40" width="70" height="14" fill="#FF6B35" rx="4"/>
  <text x="118" y="74" font-family="JetBrains Mono, monospace" font-size="8" fill="#1A1A1A" font-weight="700">SKILL.md</text>
  <text x="118" y="110" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A">xlsx/</text>
  <!-- file 3 -->
  <rect x="190" y="40" width="70" height="80" rx="4" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <rect x="190" y="40" width="70" height="14" fill="#FF6B35" rx="4"/>
  <text x="198" y="74" font-family="JetBrains Mono, monospace" font-size="8" fill="#1A1A1A" font-weight="700">SKILL.md</text>
  <text x="198" y="110" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A">docx/</text>
</svg>
```

## /compact — Compressed documents

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <!-- big stack -->
  <rect x="40" y="30" width="70" height="90" rx="4" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <line x1="52" y1="50" x2="98" y2="50" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="52" y1="62" x2="98" y2="62" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="52" y1="74" x2="92" y2="74" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="52" y1="86" x2="98" y2="86" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="52" y1="98" x2="88" y2="98" stroke="#1A1A1A" stroke-width="1.5"/>
  <!-- arrow / x -->
  <line x1="130" y1="60" x2="155" y2="85" stroke="#FF6B35" stroke-width="3" stroke-linecap="round"/>
  <line x1="155" y1="60" x2="130" y2="85" stroke="#FF6B35" stroke-width="3" stroke-linecap="round"/>
  <!-- summary -->
  <rect x="175" y="55" width="70" height="40" rx="4" fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2"/>
  <text x="183" y="80" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A" font-weight="700">SUMMARY</text>
</svg>
```

## /security-review — Shield with vulnerability tags

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <!-- tags scattered -->
  <text x="30" y="40" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="500">SQLi</text>
  <text x="30" y="68" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="500">XSS</text>
  <text x="30" y="96" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="500">secrets</text>
  <text x="30" y="124" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="500">auth</text>
  <!-- shield -->
  <path d="M140 30 L180 45 L180 80 Q180 105 140 120 Q100 105 100 80 L100 45 Z"
        fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2.5" stroke-linejoin="round"/>
  <polyline points="120,78 135,93 162,66" fill="none" stroke="#FF6B35" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- tags right -->
  <text x="210" y="40" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="500">CSRF</text>
  <text x="210" y="68" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="500">XXE</text>
  <text x="210" y="96" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="500">tokens</text>
  <text x="210" y="124" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="500">RCE</text>
</svg>
```

## /agents — Subagent network graph

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <!-- connecting lines -->
  <line x1="140" y1="70" x2="60" y2="35" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="140" y1="70" x2="60" y2="105" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="140" y1="70" x2="220" y2="35" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="140" y1="70" x2="220" y2="105" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="140" y1="70" x2="140" y2="20" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="140" y1="70" x2="140" y2="120" stroke="#1A1A1A" stroke-width="1.5"/>
  <!-- outer nodes -->
  <circle cx="60" cy="35" r="9" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="60" cy="105" r="9" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="220" cy="35" r="9" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="220" cy="105" r="9" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="140" cy="20" r="9" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <circle cx="140" cy="120" r="9" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <!-- central node -->
  <circle cx="140" cy="70" r="16" fill="#FF6B35" stroke="#1A1A1A" stroke-width="2"/>
  <text x="140" y="74" font-family="JetBrains Mono, monospace" font-size="9" fill="#FFFFFF" font-weight="700" text-anchor="middle">main</text>
</svg>
```

## /hooks — Pre/post pipeline

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <!-- PRE block -->
  <rect x="20" y="50" width="60" height="40" rx="6" fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2"/>
  <text x="50" y="74" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="700" text-anchor="middle">PRE</text>
  <!-- arrow -->
  <line x1="85" y1="70" x2="105" y2="70" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
  <polyline points="98,64 105,70 98,76" fill="none" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- TOOL block -->
  <rect x="110" y="50" width="60" height="40" rx="6" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <text x="140" y="74" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="700" text-anchor="middle">TOOL</text>
  <!-- arrow -->
  <line x1="175" y1="70" x2="195" y2="70" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
  <polyline points="188,64 195,70 188,76" fill="none" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- POST block -->
  <rect x="200" y="50" width="60" height="40" rx="6" fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2"/>
  <text x="230" y="74" font-family="JetBrains Mono, monospace" font-size="11" fill="#1A1A1A" font-weight="700" text-anchor="middle">POST</text>
  <!-- labels below -->
  <text x="50" y="108" font-family="JetBrains Mono, monospace" font-size="9" fill="#3F3F50" text-anchor="middle">prettier · lint</text>
  <text x="230" y="108" font-family="JetBrains Mono, monospace" font-size="9" fill="#3F3F50" text-anchor="middle">tsc · tests</text>
</svg>
```

## /mcp — External tools connector

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <!-- center claude node -->
  <rect x="105" y="55" width="70" height="30" rx="6" fill="#FF6B35" stroke="#1A1A1A" stroke-width="2"/>
  <text x="140" y="75" font-family="JetBrains Mono, monospace" font-size="10" fill="#FFFFFF" font-weight="700" text-anchor="middle">Claude</text>
  <!-- spokes -->
  <line x1="105" y1="70" x2="55" y2="35" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="105" y1="70" x2="55" y2="105" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="175" y1="70" x2="225" y2="35" stroke="#1A1A1A" stroke-width="1.5"/>
  <line x1="175" y1="70" x2="225" y2="105" stroke="#1A1A1A" stroke-width="1.5"/>
  <!-- outer nodes -->
  <rect x="15" y="22" width="60" height="26" rx="6" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <text x="45" y="40" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A" font-weight="700" text-anchor="middle">GitHub</text>
  <rect x="15" y="92" width="60" height="26" rx="6" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <text x="45" y="110" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A" font-weight="700" text-anchor="middle">Postgres</text>
  <rect x="205" y="22" width="60" height="26" rx="6" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <text x="235" y="40" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A" font-weight="700" text-anchor="middle">Slack</text>
  <rect x="205" y="92" width="60" height="26" rx="6" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <text x="235" y="110" font-family="JetBrains Mono, monospace" font-size="9" fill="#1A1A1A" font-weight="700" text-anchor="middle">Browser</text>
</svg>
```

## Generic concepts

### Idea / lightbulb concept (for "tip" or "insight" cards)

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <circle cx="140" cy="60" r="28" fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2.5"/>
  <rect x="130" y="86" width="20" height="6" fill="#1A1A1A" rx="1"/>
  <rect x="132" y="94" width="16" height="4" fill="#1A1A1A" rx="1"/>
  <!-- rays -->
  <line x1="140" y1="15" x2="140" y2="25" stroke="#FF6B35" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="105" y1="30" x2="112" y2="37" stroke="#FF6B35" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="175" y1="30" x2="168" y2="37" stroke="#FF6B35" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="90" y1="60" x2="100" y2="60" stroke="#FF6B35" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="190" y1="60" x2="180" y2="60" stroke="#FF6B35" stroke-width="2.5" stroke-linecap="round"/>
</svg>
```

### Workflow steps (numbered)

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="70" r="18" fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2"/>
  <text x="50" y="75" font-family="Satoshi, Geist, system-ui, sans-serif" font-size="14" fill="#1A1A1A" font-weight="800" text-anchor="middle">1</text>
  <line x1="68" y1="70" x2="122" y2="70" stroke="#1A1A1A" stroke-width="2" stroke-dasharray="3 4"/>
  <circle cx="140" cy="70" r="18" fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2"/>
  <text x="140" y="75" font-family="Satoshi, Geist, system-ui, sans-serif" font-size="14" fill="#1A1A1A" font-weight="800" text-anchor="middle">2</text>
  <line x1="158" y1="70" x2="212" y2="70" stroke="#1A1A1A" stroke-width="2" stroke-dasharray="3 4"/>
  <circle cx="230" cy="70" r="18" fill="#FF6B35" stroke="#1A1A1A" stroke-width="2"/>
  <text x="230" y="75" font-family="Satoshi, Geist, system-ui, sans-serif" font-size="14" fill="#FFFFFF" font-weight="800" text-anchor="middle">3</text>
</svg>
```

### Comparison / vs

```svg
<svg viewBox="0 0 280 140" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="30" width="100" height="80" rx="6" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/>
  <text x="70" y="65" font-family="Satoshi, Geist, system-ui, sans-serif" font-size="13" fill="#1A1A1A" font-weight="800" text-anchor="middle">OLD</text>
  <text x="70" y="84" font-family="JetBrains Mono, monospace" font-size="9" fill="#3F3F50" text-anchor="middle">manual</text>
  <text x="140" y="78" font-family="Satoshi, Geist, system-ui, sans-serif" font-size="18" fill="#FF6B35" font-weight="900" text-anchor="middle">/</text>
  <rect x="160" y="30" width="100" height="80" rx="6" fill="#FFE8DA" stroke="#1A1A1A" stroke-width="2"/>
  <text x="210" y="65" font-family="Satoshi, Geist, system-ui, sans-serif" font-size="13" fill="#1A1A1A" font-weight="800" text-anchor="middle">NEW</text>
  <text x="210" y="84" font-family="JetBrains Mono, monospace" font-size="9" fill="#3F3F50" text-anchor="middle">automated</text>
</svg>
```

## When the concept doesn't match a pre-built illustration

If the source content covers a concept not in this library, build a new illustration following these rules:

1. Identify the core verb of the concept (e.g., "compress" → arrows pointing inward; "extend" → arrows pointing outward; "connect" → line between two nodes)
2. Pick 2-3 basic shapes (rectangles for things, circles for nodes/concepts, lines for relationships)
3. One element gets the orange accent (highlight what matters most)
4. Keep stroke width consistent (2-2.5px)
5. Don't add gratuitous detail — these are diagrams, not illustrations

Aim for something that reads in 1 second at thumbnail size.
