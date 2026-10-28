# CardVault

A single-user, **no-backend** web app for scanning, cataloguing, grading and "slabbing" trading & sports cards.
Static HTML/CSS/JS only – no server, no login. All data stays in your browser (localStorage + IndexedDB).

## Run it
Camera access needs `https://` or `localhost`:

```
python3 -m http.server 8000     # then open http://localhost:8000
```
or publish the folder on GitHub Pages / Netlify / any static host.

## Features
- **Scan**: pick any camera; **Fast slide** mode auto-captures each card as you slide it in; **Manual** mode with review/retake; **Upload** scans (bulk). Front only or front + back.
- **Auto-identify** (TCG): in-browser OCR (Tesseract.js) + free card databases – Pokémon (pokemontcg.io), Magic (Scryfall), Yu-Gi-Oh! (YGOPRODeck) – for full stats, prices and HQ art. Sports cards (baseball, basketball, football, hockey, soccer, golf, …) use manual fields.
- **Collection**: search/filter/sort, edit, export **CSV / Excel**, listing sheet, full JSON backup/restore.
- **Slab Studio**: choose a scan, an upload or a web HQ image → estimated grade (centering/corners/edges/surface, adjustable) → branded label (your logo, colours, font) at exact print size, transparent-background slab PNG/JPG, and slab + info sheet as PDF/PNG/JPG/WebP.
- **eBay / CollX**: those sites can't be posted to from a serverless page, so the app builds title/description/photos and opens their listing page.

Grades are automated estimates, not PSA/BGS/SGC grades.
