# Changes Summary - Extract Watermark Script

## What Changed?

The `extract_watermark.py` script has been modified to **always assume supplied watermarked images are altered** and automatically perform recovery by comparing with the original image.

## Key Changes

### 1. **Recovery-First Approach** (New Default Behavior)
- **Before**: Script tried direct extraction first, then recovery if that failed
- **After**: Script immediately uses recovery-based extraction when original image is available
- This aligns with your use case where images are typically cropped, screenshot, or modified

### 2. **Configuration Changes**
```python
# OLD
ENABLE_RECOVERY = True  # Set to False to skip recovery attempt

# NEW  
ALWAYS_USE_RECOVERY = True  # Always attempt recovery when original image is available
```

### 3. **Improved Workflow**
```python
# Now when you run the script with these settings:
WATERMARKED_IMAGE = 'examples/output/watermarked2.png'  # Your altered image
ORIGINAL_WATERMARKED_IMAGE = 'examples/output/watermarked.png'  # Reference image
ALWAYS_USE_RECOVERY = True  # Default

# The script will:
# 1. ✓ Immediately assume the image is altered
# 2. ✓ Compare with original to detect modifications
# 3. ✓ Automatically recover the image
# 4. ✓ Extract the watermark from recovered image
# 5. ✓ Show quality score and recovery details
```

## New Features

### Quality Scoring
The script now provides interpretation of the recovery quality:
```
- Quality: Excellent (score > 0.95) ✓
- Quality: Good (score > 0.85) ✓
- Quality: Fair (score > 0.70) ⚠
- Quality: Poor (score < 0.70) ⚠ - Extraction may be unreliable
```

### Better Diagnostics
More detailed recovery information:
```
📊 Recovery Information:
  - Recovered image saved to: watermarked2_recovered.png
  - Detected crop region: (100, 50, 400, 350)
  - Scale factor: 0.7500
  - Match score: 0.9823
  - Quality: Excellent (score > 0.95) ✓
```

### Helpful Suggestions
If recovery fails, the script now suggests adjustments:
```
💡 Try adjusting recovery settings:
  - Increase SEARCH_NUM for better accuracy
  - Adjust SCALE_RANGE if image was heavily resized
```

## Usage Comparison

### Before (Two-Stage Approach)
```
1. Try direct extraction → Fail
2. Detect failure
3. Try recovery → Success
```

### After (Recovery-First Approach)
```
1. Assume image is altered (your requirement)
2. Use recovery immediately → Success
```

## When to Use Each Approach

### Use Recovery-First (Default - ALWAYS_USE_RECOVERY = True)
✅ Images are typically cropped/screenshot/modified
✅ You always have the original watermarked image
✅ You want maximum reliability
✅ Your workflow expects alterations

### Use Direct Extraction (ALWAYS_USE_RECOVERY = False)
⚠ Images are never modified
⚠ You don't have the original image
⚠ You need faster processing (no recovery overhead)

## Example Workflow

```bash
# Step 1: Embed watermark
python embed_watermark.py
# Saves: examples/output/watermarked.png
# Output: Watermark length: 63

# Step 2: User crops/screenshots the watermarked image
# Result: examples/output/watermarked2.png (cropped version)

# Step 3: Configure extraction script
# Set in extract_watermark.py:
WATERMARKED_IMAGE = 'examples/output/watermarked2.png'  # Altered
ORIGINAL_WATERMARKED_IMAGE = 'examples/output/watermarked.png'  # Original
ALWAYS_USE_RECOVERY = True  # Assumes image is altered
WATERMARK_LENGTH = 63

# Step 4: Extract watermark
python extract_watermark.py

# Output:
# 🔄 Assuming image has been altered (cropped/screenshot/extended)
# 🔄 Using recovery-based extraction...
# 
# --- Starting Recovery Process ---
# Estimating attack parameters...
# Detected parameters:
#   - Crop region: x1=..., y1=..., x2=..., y2=...
#   - Scale factor: 0.75
#   - Match score: 0.98
# 
# ✓ SUCCESS! Watermark extracted after recovery!
# ✓ Extracted text: v-5.37.2
```

## Benefits of This Approach

1. **Aligns with your use case**: Assumes all images are altered
2. **More efficient**: Skips unnecessary direct extraction attempt
3. **Better diagnostics**: Always shows how image was modified
4. **Quality feedback**: Provides confidence score for extraction
5. **Transparent**: Shows exactly what modifications were detected

## Backward Compatibility

The script still supports direct extraction as a fallback:
- If `ORIGINAL_WATERMARKED_IMAGE` is not provided → Direct extraction
- If `ORIGINAL_WATERMARKED_IMAGE` equals `WATERMARKED_IMAGE` → Direct extraction
- If `ALWAYS_USE_RECOVERY = False` → Direct extraction

## Files Modified

1. **extract_watermark.py**
   - Changed default behavior to recovery-first
   - Added quality scoring and interpretation
   - Improved error messages and suggestions
   
2. **WATERMARK_USAGE.md**
   - Updated to reflect new recovery-first approach
   - Added quality score interpretation
   - Clarified primary use case (altered images)

3. **CHANGES_SUMMARY.md** (this file)
   - Documents all changes
   - Provides usage comparison
   - Explains the new approach

