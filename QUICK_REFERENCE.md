# Quick Reference - Watermark Extraction with Auto-Recovery

## TL;DR - Quick Start

```python
# 1. In extract_watermark.py, configure:
WATERMARKED_IMAGE = 'path/to/your/cropped_or_screenshot.png'  # Altered image
ORIGINAL_WATERMARKED_IMAGE = 'path/to/original/watermarked.png'  # Reference
WATERMARK_LENGTH = 63  # From embedding step
ALWAYS_USE_RECOVERY = True  # Default - assumes image is altered

# 2. Run:
python extract_watermark.py

# 3. Done! The script automatically:
#    - Detects how the image was modified
#    - Recovers the image to original dimensions
#    - Extracts the watermark
#    - Shows quality score
```

## What It Does

**Assumes all supplied images are altered** and automatically compares with the original to:
- Detect crop region
- Detect scale changes
- Recover image to original dimensions
- Extract watermark reliably

## Configuration Quick Reference

| Setting | Value | Purpose |
|---------|-------|---------|
| `WATERMARKED_IMAGE` | Path to altered image | The image you want to extract from |
| `ORIGINAL_WATERMARKED_IMAGE` | Path to original | Reference for comparison/recovery |
| `WATERMARK_LENGTH` | Number (e.g., 63) | From embedding step |
| `ALWAYS_USE_RECOVERY` | `True` (default) | Always use recovery when possible |
| `SCALE_RANGE` | `(0.5, 2)` | Range to search for scale changes |
| `SEARCH_NUM` | `200` | Accuracy vs speed (higher = slower) |

## Common Scenarios

### Scenario 1: Screenshot of Watermarked Image
```python
WATERMARKED_IMAGE = 'screenshot.png'
ORIGINAL_WATERMARKED_IMAGE = 'original_watermarked.png'
SCALE_RANGE = (0.5, 2)  # Wide range for different screen sizes
```

### Scenario 2: Cropped Image (No Scaling)
```python
WATERMARKED_IMAGE = 'cropped.png'
ORIGINAL_WATERMARKED_IMAGE = 'original_watermarked.png'
SCALE_RANGE = (1, 1)  # No scaling, just crop
SEARCH_NUM = None  # Exhaustive search
```

### Scenario 3: Heavily Modified Image
```python
WATERMARKED_IMAGE = 'heavily_modified.png'
ORIGINAL_WATERMARKED_IMAGE = 'original_watermarked.png'
SCALE_RANGE = (0.3, 3)  # Very wide range
SEARCH_NUM = 500  # More iterations for better accuracy
```

## Understanding Output

### Successful Extraction
```
✓ SUCCESS! Watermark extracted after recovery!
✓ Extracted text: v-5.37.2
  - Quality: Excellent (score > 0.95) ✓
```
✅ **Action**: The extraction is reliable, use the result

### Good Extraction
```
✓ SUCCESS! Watermark extracted after recovery!
✓ Extracted text: v-5.37.2
  - Quality: Good (score > 0.85) ✓
```
✅ **Action**: The extraction is reliable, use the result

### Fair Extraction
```
✓ SUCCESS! Watermark extracted after recovery!
✓ Extracted text: v-5.37.2
  - Quality: Fair (score > 0.70) ⚠
```
⚠ **Action**: Result may be usable, but verify if possible

### Poor Extraction
```
✓ SUCCESS! Watermark extracted after recovery!
✓ Extracted text: ???
  - Quality: Poor (score < 0.70) ⚠ - Extraction may be unreliable
```
❌ **Action**: Try adjusting SEARCH_NUM or SCALE_RANGE

## Troubleshooting

### "Recovery-based extraction failed"
**Problem**: Image was modified too severely or wrong settings

**Solutions**:
1. Increase `SEARCH_NUM = 500` for better accuracy
2. Widen `SCALE_RANGE = (0.3, 3)` for extreme scaling
3. Verify `ORIGINAL_WATERMARKED_IMAGE` is correct
4. Check `WATERMARK_LENGTH` matches embedding

### "No original image provided"
**Problem**: `ORIGINAL_WATERMARKED_IMAGE` not set or doesn't exist

**Solutions**:
1. Set `ORIGINAL_WATERMARKED_IMAGE` to correct path
2. Make sure file exists
3. Ensure it's different from `WATERMARKED_IMAGE`

### Low Quality Score (< 0.70)
**Problem**: Image matching is poor

**Solutions**:
1. Increase `SEARCH_NUM` for more thorough search
2. Adjust `SCALE_RANGE` based on known scaling
3. Image may have multiple attacks (crop + rotate + compress)
4. Original image may be incorrect

## Performance Tuning

### Fast (Less Accurate)
```python
SEARCH_NUM = 50
SCALE_RANGE = (0.8, 1.2)  # Narrow range
```

### Balanced (Recommended)
```python
SEARCH_NUM = 200  # Default
SCALE_RANGE = (0.5, 2)  # Default
```

### Slow (Most Accurate)
```python
SEARCH_NUM = 500
SCALE_RANGE = (0.3, 3)
```

## Complete Workflow

```bash
# Step 1: Embed watermark (one-time setup)
python embed_watermark.py
# Note the watermark length (e.g., 63)

# Step 2: Image gets altered (user action)
# User crops, screenshots, or modifies the watermarked image

# Step 3: Configure extraction
# Edit extract_watermark.py:
WATERMARKED_IMAGE = 'altered_image.png'
ORIGINAL_WATERMARKED_IMAGE = 'watermarked.png'
WATERMARK_LENGTH = 63  # From step 1

# Step 4: Extract
python extract_watermark.py
# Script automatically handles recovery
```

## Key Points

✅ **Always keep** the original watermarked image for recovery
✅ **Script assumes** images are altered by default
✅ **Quality score** tells you if extraction is reliable
✅ **Adjust settings** based on how image was modified
✅ **Recovery works** for crop, scale, screenshot, extend
❌ **May fail** with multiple severe attacks (rotate + crop + heavy compression)

## Need More Details?

- See **WATERMARK_USAGE.md** for comprehensive documentation
- See **CHANGES_SUMMARY.md** for what changed
- See **extract_watermark.py** comments for parameter details

