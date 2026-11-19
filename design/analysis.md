---
title: World in Brief — 19 November 2026
topic: public-interest world news
data_type: overview with explicit editorial hierarchy
complexity: moderate
point_count: 6
source_language: English and Japanese
user_language: Indonesian
artwork_language: English
---

# Design and editorial analysis

## Main topic and viewer goals

A six-story early edition, explicitly frozen at 04:00 UTC on 19 November 2026. The viewer should identify the date, understand the main developments, and distinguish an attributed report, a forecast and a preliminary measurement from an established final outcome. This is a Monitor surface, not a marketing landing page.

## Source data integrity

The canonical claim and caveat records are in `../news.json`; exact source attribution and date reasoning are in `../SOURCES.md`. Critical strings retained without rounding: 4.9%, M5.7, 02:22 JST, October, 20 Nov (forecast), 19 NOV 2026 and 04:00 UTC. No summit agreement, bridge damage count, cyclone casualty number or global-completion claim was invented.

## Combinations considered

1. Editorial bento + bold graphic: strong hierarchy, but exaggerated comic effects would be inappropriate for war and severe weather.
2. **Editorial bento + retro-pop-grid — selected:** a restrained Swiss grid, warm newsprint, flat color, black rules and original symbols. The serious editorial tone takes precedence over decorative pop-art effects.
3. Dense modules + pop-laboratory: rejected as the default because small text and more equal-sized boxes would impair the requested small-view readability.

## Actual system

- Canvas: 1024 × 1024, RGB PNG; 2× supersampled development render.
- Palette: warm paper #F5F0E6, ink #151A1B, rust #B93F31, muted gold #E2BD71, dark teal #285E5A.
- Noto Serif Display SemiCondensed ExtraBold for the masthead and news anchors; Noto Sans for supporting text. Font assets and their license are bundled.
- One full-width lead, two middle stories, three short supporting stories. No rounded SaaS cards, gradients, 3D rendering or copied publication branding.
- Generic figures inside a photo viewfinder represent the APEC group photo; an intact bridge with a stop symbol avoids depicting unverified destruction. The cyclone is a symbol, not a fabricated track chart. The gamepad is generic, not game character art.

## Quality gates

`layout-audit.json` contains the measured text bounding boxes and chosen font sizes. The renderer fails when text cannot fit its assigned width or leaves the canvas. `preview-300.png` is a real downscale, not a separately redrawn thumbnail. Independent visual review was requested; this document does not claim a review result before it is actually received.
