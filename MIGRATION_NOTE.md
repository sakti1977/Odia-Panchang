# Database Migration Required - May 2026

## Issue Fixed
The Purnimanta lunar month calculation had an error that caused incorrect month names to be displayed. For example, May 10, 2026 was incorrectly showing as "Chaitra Krishna Ashtami" when it should be "Jyeshtha Krishna Ashtami".

## What Was Fixed
1. **Lunar Month Calculation**: Corrected the `_chandra_masa_index` function in `src/engine.py` to properly implement the Purnimanta system used in Odisha. The formula now correctly maps solar months to lunar months with the empirically verified offset: `Chandra Masa Index = (Soura Masa Index + 2) % 12`

2. **Default Location**: Changed from Bangalore to Bhubaneswar (capital of Odisha) for accurate sunrise/sunset and muhurta timings

3. **AI Enrichment**: Strengthened the Claude AI prompt to prevent fabrication of spiritual descriptions and temple rituals

## Action Required
**The existing database (`data/panchang.db`) contains data computed with the old (incorrect) lunar month calculation.**

To fix this, you need to reseed the database:

```bash
# Backup the old database (optional)
cp data/panchang.db data/panchang.db.backup

# Delete the old database
rm data/panchang.db

# Reseed with corrected calculations (adjust years as needed)
python3 seed.py --start 2020 --end 2030
```

## Verification
After reseeding, verify key dates:
- March 11, 2026: Should show **Chaitra** Krishna Ashtami ✓
- May 10, 2026: Should show **Jyeshtha** Krishna Ashtami ✓

## Impact
- **Web API**: Will automatically use new calculations after restarting
- **Twitter Bot**: Will post accurate Panchang data after restart
- **Existing Database**: Needs manual reseed (see above)
