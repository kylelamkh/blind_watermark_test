# Watermark Extraction with Recovery

## Overview

The enhanced `extract_watermark.py` script **assumes all supplied images are altered** and automatically performs recovery by comparing with the original watermarked image. It supports recovery for images that have been:
- **Cropped** (parts removed)
- **Screenshot** (with scaling/resolution changes)
- **Extended** (with padding added)
- **Resized** (scaled up or down)

## How It Works

The script uses an **intelligent recovery-first approach**:

1. **Recovery-Based Extraction** (Default) - When an original reference image is available:
   - Automatically detects how the image was modified (crop region, scale factor)
   - Restores the image to its original dimensions
   - Extracts the watermark from the restored image
   - Provides quality score and recovery details

2. **Direct Extraction** (Fallback) - Only when no original image is available:
   - Attempts direct extraction without recovery
   - Less reliable for altered images

## Configuration

### Basic Settings
```python
WATERMARKED_IMAGE = 'examples/output/watermarked2.png'  # The altered image to extract from
ORIGINAL_WATERMARKED_IMAGE = 'examples/output/watermarked.png'  # Original reference image
WATERMARK_LENGTH = 63  # Must match the value from embedding
PASSWORD_IMG = 1  # Must match embedding password
PASSWORD_WM = 1   # Must match embedding password
```

### Recovery Settings
```python
ALWAYS_USE_RECOVERY = True  # Always attempt recovery when original image is available (recommended)
SCALE_RANGE = (0.5, 2)  # Range of scale factors to search
SEARCH_NUM = 200  # Search iterations (higher = more accurate but slower)
```

**Important:** The script now assumes all supplied watermarked images are altered and will automatically compare them with the original image to recover and extract the watermark.

## Usage Examples

### Example 1: Altered Image (Primary Use Case)
The script assumes your image has been cropped, screenshot, or modified:

```python
WATERMARKED_IMAGE = 'examples/output/watermarked_cropped.png'  # Your altered image
ORIGINAL_WATERMARKED_IMAGE = 'examples/output/watermarked.png'  # Original for reference
ALWAYS_USE_RECOVERY = True  # This is the default
WATERMARK_LENGTH = 63
```

**Output:**
```
🔄 Assuming image has been altered (cropped/screenshot/extended)
🔄 Using recovery-based extraction...

--- Starting Recovery Process ---
Estimating attack parameters...
Detected parameters:
  - Crop region: x1=100, y1=50, x2=400, y2=350
  - Scale factor: 0.7500
  - Match score: 0.9823

✓ SUCCESS! Watermark extracted after recovery!
✓ Extracted text: v-5.37.2
📊 Recovery Information:
  - Quality: Excellent (score > 0.95) ✓
```

### Example 2: Unmodified Image (Fallback)
If you don't have the original image (rare case):

```python
WATERMARKED_IMAGE = 'watermarked.png'
ORIGINAL_WATERMARKED_IMAGE = None  # Or same as WATERMARKED_IMAGE
# Will fall back to direct extraction
```

**Output:**
```
⚠ No original image provided
⚠ Attempting direct extraction (without recovery)...
✓ SUCCESS! Watermark extracted directly!
✓ Extracted text: v-5.37.2
```

## Functions

### `extract_watermark(watermarked_img, wm_length, pwd_img=1, pwd_wm=1)`
Direct extraction without recovery. Use for unmodified images.

**Returns:** Extracted watermark string

### `extract_with_recovery(attacked_img, original_img, wm_length, ...)`
Extraction with automatic recovery for modified images.

**Returns:** Tuple of (extracted_text, recovery_info_dict)

## Important Notes

### When Recovery Works
✅ Cropped images (parts removed)
✅ Screenshot with scaling
✅ Extended/padded images
✅ Combination of crop + scale

### When Recovery May Fail
❌ Multiple severe modifications (e.g., crop + rotate + heavy compression)
❌ Wrong original image provided
❌ Extreme compression or quality loss
❌ Image re-encoded with very different parameters

### Tips for Best Results

1. **Keep the original watermarked image** - You'll need it for recovery
2. **Higher SEARCH_NUM** - More accurate but slower (default: 200)
3. **Adjust SCALE_RANGE** - If you know the image was resized significantly
4. **Check match score** - Higher score (>0.95) indicates better recovery

## Workflow Example

```bash
# 1. Embed watermark into original image
python embed_watermark.py
# Output: Watermark length: 63

# 2. The watermarked image gets cropped/screenshot/modified
# (manually by user or through some process)

# 3. Configure extract_watermark.py for recovery
# In extract_watermark.py:
WATERMARKED_IMAGE = 'cropped_or_screenshot_image.png'  # The altered image
ORIGINAL_WATERMARKED_IMAGE = 'watermarked.png'  # Original watermarked image
ALWAYS_USE_RECOVERY = True  # This is default - assumes image is altered
WATERMARK_LENGTH = 63  # From step 1

# 4. Extract with automatic recovery
python extract_watermark.py
# Script automatically detects modifications and recovers the image
```

## Key Features

✅ **Assumes all images are altered** - No need to try direct extraction first
✅ **Automatic parameter detection** - Detects crop region and scale automatically
✅ **Quality scoring** - Tells you how reliable the extraction is
✅ **Saves recovered image** - For manual inspection if needed
✅ **Detailed diagnostics** - Shows what modifications were detected

## Recovery Quality Scores

The script provides a match score to indicate extraction reliability:

- **Score > 0.95**: Excellent - Extraction is highly reliable ✓
- **Score > 0.85**: Good - Extraction is reliable ✓
- **Score > 0.70**: Fair - Extraction may have minor issues ⚠
- **Score < 0.70**: Poor - Extraction may be unreliable ⚠

## Recovery Settings Guide

### For Screenshots
```python
SCALE_RANGE = (0.5, 2)  # Wide range for various screen sizes
SEARCH_NUM = 200  # Good balance
```

### For Small Crops
```python
SCALE_RANGE = (1, 1)  # No scaling, just crop
SEARCH_NUM = None  # Exhaustive search
```

### For Severe Modifications
```python
SCALE_RANGE = (0.3, 3)  # Very wide range
SEARCH_NUM = 500  # More iterations
```

## Limitations

This is a frequency-domain watermarking technique, which means:

- **Requires same dimensions** for direct extraction
- **Requires original image** for recovery-based extraction
- **May fail** with multiple severe attacks (rotation + crop + compression)
- **Screenshot quality matters** - too much compression can corrupt the watermark

For maximum robustness, keep a copy of the original watermarked image and use the recovery features when needed.

