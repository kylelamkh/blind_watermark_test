#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate the recovery-based watermark extraction
This creates test cases to show how the extraction works with altered images
"""
import os
import cv2
from blind_watermark import WaterMark
from blind_watermark import att

def test_extraction_workflow():
    """
    Complete workflow demonstration:
    1. Embed watermark
    2. Create altered versions (crop, screenshot simulation)
    3. Extract with recovery
    """
    
    print("="*70)
    print("WATERMARK EXTRACTION WITH RECOVERY - TEST SCRIPT")
    print("="*70)
    
    # Configuration
    INPUT_IMAGE = 'examples/pic/ori_img.jpeg'
    WATERMARK_TEXT = 'v-5.37.2'
    PASSWORD_IMG = 1
    PASSWORD_WM = 1
    
    # Step 1: Embed watermark
    print("\n[Step 1] Embedding watermark...")
    output_dir = 'examples/output'
    os.makedirs(output_dir, exist_ok=True)
    
    original_watermarked = os.path.join(output_dir, 'test_watermarked_original.png')
    
    bwm = WaterMark(password_img=PASSWORD_IMG, password_wm=PASSWORD_WM)
    bwm.read_img(INPUT_IMAGE)
    bwm.read_wm(WATERMARK_TEXT, mode='str')
    bwm.embed(original_watermarked)
    len_wm = len(bwm.wm_bit)
    
    print(f"✓ Original watermarked image saved: {original_watermarked}")
    print(f"✓ Watermark length: {len_wm}")
    
    # Get original image shape for recovery
    ori_img_shape = cv2.imread(INPUT_IMAGE).shape[:2]
    h, w = ori_img_shape
    print(f"✓ Original shape: {ori_img_shape}")
    
    # Step 2: Create altered versions
    print("\n[Step 2] Creating altered test images...")
    
    # Test Case 1: Simple crop (no scaling)
    print("\n  Test Case 1: Simple Crop")
    cropped_img = os.path.join(output_dir, 'test_cropped.png')
    x1, y1, x2, y2 = int(w * 0.1), int(h * 0.1), int(w * 0.7), int(h * 0.7)
    att.cut_att3(input_filename=original_watermarked, output_file_name=cropped_img,
                 loc=(x1, y1, x2, y2), scale=None)
    print(f"  ✓ Cropped image created: {cropped_img}")
    print(f"    Crop region: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    
    # Test Case 2: Screenshot simulation (crop + scale)
    print("\n  Test Case 2: Screenshot Simulation (Crop + Scale)")
    screenshot_img = os.path.join(output_dir, 'test_screenshot.png')
    x1, y1, x2, y2 = int(w * 0.15), int(h * 0.15), int(w * 0.85), int(h * 0.85)
    scale = 0.7
    att.cut_att3(input_filename=original_watermarked, output_file_name=screenshot_img,
                 loc=(x1, y1, x2, y2), scale=scale)
    print(f"  ✓ Screenshot image created: {screenshot_img}")
    print(f"    Crop region: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    print(f"    Scale factor: {scale}")
    
    # Step 3: Extract from altered images using recovery
    print("\n[Step 3] Extracting watermarks with recovery...")
    
    from extract_watermark import extract_with_recovery
    
    # Test Case 1: Extract from cropped image
    print("\n  Test Case 1: Extracting from cropped image...")
    try:
        extracted_text, recovery_info = extract_with_recovery(
            attacked_img=cropped_img,
            original_img=original_watermarked,
            wm_length=len_wm,
            pwd_img=PASSWORD_IMG,
            pwd_wm=PASSWORD_WM,
            scale_range=(1, 1),  # No scaling expected
            search_num=None  # Exhaustive search for crop-only
        )
        
        print(f"\n  ✓ Extraction SUCCESS!")
        print(f"  ✓ Extracted text: {extracted_text}")
        print(f"  ✓ Match score: {recovery_info['match_score']:.4f}")
        
        if extracted_text == WATERMARK_TEXT:
            print(f"  ✓ VERIFIED: Extracted text matches original watermark!")
        else:
            print(f"  ✗ WARNING: Extracted text doesn't match!")
            print(f"    Expected: {WATERMARK_TEXT}")
            print(f"    Got: {extracted_text}")
    except Exception as e:
        print(f"  ✗ Extraction failed: {e}")
    
    # Test Case 2: Extract from screenshot
    print("\n  Test Case 2: Extracting from screenshot simulation...")
    try:
        extracted_text, recovery_info = extract_with_recovery(
            attacked_img=screenshot_img,
            original_img=original_watermarked,
            wm_length=len_wm,
            pwd_img=PASSWORD_IMG,
            pwd_wm=PASSWORD_WM,
            scale_range=(0.5, 2),  # Wider range for scaling
            search_num=200
        )
        
        print(f"\n  ✓ Extraction SUCCESS!")
        print(f"  ✓ Extracted text: {extracted_text}")
        print(f"  ✓ Match score: {recovery_info['match_score']:.4f}")
        print(f"  ✓ Detected scale: {recovery_info['scale_factor']:.4f}")
        
        if extracted_text == WATERMARK_TEXT:
            print(f"  ✓ VERIFIED: Extracted text matches original watermark!")
        else:
            print(f"  ✗ WARNING: Extracted text doesn't match!")
            print(f"    Expected: {WATERMARK_TEXT}")
            print(f"    Got: {extracted_text}")
    except Exception as e:
        print(f"  ✗ Extraction failed: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print(f"  - Original watermarked: {original_watermarked}")
    print(f"  - Test cropped: {cropped_img}")
    print(f"  - Test screenshot: {screenshot_img}")
    print(f"  - Recovered images: *_recovered.png")
    print("\nYou can now use extract_watermark.py with these test images!")
    print(f"\nExample configuration:")
    print(f"  WATERMARKED_IMAGE = '{cropped_img}'")
    print(f"  ORIGINAL_WATERMARKED_IMAGE = '{original_watermarked}'")
    print(f"  WATERMARK_LENGTH = {len_wm}")

if __name__ == '__main__':
    try:
        test_extraction_workflow()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

