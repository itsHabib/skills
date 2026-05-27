---
name: status
description: Produce a tight 4-section status update (What happened / What's next / What I recommend / What I need from you), 1-3 sentences each. Use when the user says "give me an update", "status", "where are we", "sitrep", "recap", "summarize the situation", or invokes `/status`. Skip any section that's genuinely empty rather than padding it.
---

# Status update

Output four sections, in this order, with these exact headers. **Hard cap: 1-3 sentences per section.**

## What happened
Concrete outcomes since the last update or session start — shipped / merged / blocked. PR numbers, SHAs, file paths welcome. No process narration ("I tried X then Y") — just results.

## What's next
The 1-2 immediate moves in priority order. Not a backlog dump.

## What I recommend
One specific recommendation + the reason in one phrase. No hedging. If genuinely no preference, say "no strong rec" and move on.

## What I need from you
Concrete asks only ("dashboard error", "yes/no on X"). If nothing's blocking: write "nothing — keep moving" and stop.

## Rules

- 1-3 sentences per section is a hard cap. If it won't fit, the framing is wrong, not the cap.
- Skip empty sections (no "N/A" padding).
- Write to the operator, not about the work. No "we" / "us".
- File paths / PR numbers / SHAs welcome. Adjectives and adverbs aren't.
- No emoji unless the operator's explicit style demands it.
