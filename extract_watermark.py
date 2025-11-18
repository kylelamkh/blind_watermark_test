#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to extract a string watermark from an image
Includes automatic recovery for cropped/screenshot images
"""
import os
import cv2
from blind_watermark import WaterMark
from blind_watermark.recover import estimate_crop_parameters, recover_crop

# Configuration
WATERMARKED_IMAGE = 'examples/output/vd013_background_watermarked_simulated.png'  # Path to the watermarked image (potentially cropped/screenshot)
ORIGINAL_IMAGE = 'examples/output/vd013_background_watermarked.webp'  # Path to the original watermarked image (for recovery)
WATERMARK_LENGTH = 334  # Length of watermark (from embedding process) - for 'v-5.37.2'
PASSWORD_IMG = 1  # Must match the password used during embedding
PASSWORD_WM = 1   # Must match the password used during embedding

# Recovery settings (used when ORIGINAL_WATERMARKED_IMAGE is provided)
# The script assumes all images are altered and compares with the original to recover
ALWAYS_USE_RECOVERY = True  # Always attempt recovery when original image is available
SCALE_RANGE = (0.5, 2)  # Range of scale factors to search for recovery
SEARCH_NUM = 500  # Number of search iterations for recovery (higher = more accurate but slower)

def extract_watermark(watermarked_img, wm_length, pwd_img=1, pwd_wm=1):
    """
    Extract a string watermark from an image (direct extraction, no recovery)
    
    Args:
        watermarked_img: Path to the watermarked image
        wm_length: Length of the watermark bits (from embedding process)
        pwd_img: Password for image (must match embedding password)
        pwd_wm: Password for watermark (must match embedding password)
    
    Returns:
        Extracted watermark string
    """
    # Create WaterMark instance
    bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
    
    # Extract the watermark
    wm_extract = bwm.extract(watermarked_img, wm_shape=wm_length, mode='str')
    
    return wm_extract


def extract_with_recovery(attacked_img, original_img, wm_length, pwd_img=1, pwd_wm=1, 
                          scale_range=(0.5, 2), search_num=200):
    """
    Extract watermark from a cropped/screenshot/modified image by first recovering it
    
    Args:
        attacked_img: Path to the modified/attacked image
        original_img: Path to the original watermarked image (for parameter estimation)
        wm_length: Length of the watermark bits (from embedding process)
        pwd_img: Password for image (must match embedding password)
        pwd_wm: Password for watermark (must match embedding password)
        scale_range: Tuple of (min_scale, max_scale) to search for recovery
        search_num: Number of search iterations (higher = more accurate but slower)
    
    Returns:
        Tuple of (extracted_watermark_string, recovery_info_dict)
    """
    print("\n--- Starting Recovery Process ---")
    
    # Load images to check dimensions
    attacked_image = cv2.imread(attacked_img)
    original_image = cv2.imread(original_img)
    
    attacked_h, attacked_w = attacked_image.shape[:2]
    original_h, original_w = original_image.shape[:2]
    
    print(f"Image dimensions:")
    print(f"  - Attacked/Screenshot image: {attacked_w}x{attacked_h}")
    print(f"  - Original watermarked image: {original_w}x{original_h}")
    
    # Determine if this is an extended image (screenshot with extra content) or cropped image
    is_extended = (attacked_w >= original_w or attacked_h >= original_h)
    
    if is_extended:
        print(f"\n🔍 Detected: Screenshot/Extended image (larger than original)")
        print(f"   Strategy: Find and extract the watermarked region from the larger image")
    else:
        print(f"\n🔍 Detected: Cropped image (smaller than original)")
        print(f"   Strategy: Recover original dimensions from cropped image")
    
    # Step 1: Estimate crop/scale parameters
    print("\nEstimating attack parameters...")
    (x1, y1, x2, y2), image_o_shape, score, scale_infer = estimate_crop_parameters(
        original_file=original_img,
        template_file=attacked_img,
        scale=scale_range,
        search_num=search_num
    )
    
    print(f"\nDetected parameters:")
    print(f"  - Crop/Match region: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    print(f"  - Target shape: {image_o_shape}")
    print(f"  - Scale factor: {scale_infer}")
    print(f"  - Match score: {score:.4f}")
    
    # Step 2: Recover the image to original dimensions
    # Generate recovered filename with _recovered suffix and webp extension
    base_name = os.path.splitext(attacked_img)[0]
    recovered_file = f"{base_name}_recovered.png"
    print(f"\nRecovering image to: {recovered_file}")
    
    if is_extended:
        # For extended/screenshot images: crop the region and resize to original
        print(f"  - Extracting region ({x1}:{x2}, {y1}:{y2}) from screenshot")
        print(f"  - Resizing to original dimensions: {image_o_shape}")
        
        # Crop the matched region
        cropped_region = attacked_image[y1:y2, x1:x2]
        
        # Resize to match original dimensions
        recovered_image = cv2.resize(cropped_region, (image_o_shape[1], image_o_shape[0]))
        
        # Save the recovered image
        cv2.imwrite(recovered_file, recovered_image)
    else:
        # For cropped images: use the standard recover_crop function
        print(f"  - Using standard recovery for cropped image")
        recover_crop(
            template_file=attacked_img,
            output_file_name=recovered_file,
            loc=(x1, y1, x2, y2),
            image_o_shape=image_o_shape
        )
    
    print("Recovery complete!")
    
    # Step 3: Extract watermark from recovered image
    print("Extracting watermark from recovered image...")
    bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
    wm_extract = bwm.extract(recovered_file, wm_shape=wm_length, mode='str')
    
    recovery_info = {
        'crop_region': (x1, y1, x2, y2),
        'original_shape': image_o_shape,
        'scale_factor': scale_infer,
        'match_score': score,
        'recovered_file': recovered_file
    }
    
    return wm_extract, recovery_info

if __name__ == '__main__':
    # Validate configuration
    if WATERMARK_LENGTH is None:
        print("ERROR: Please set WATERMARK_LENGTH to the value from the embedding process!")
        print("This value is printed when you run embed_watermark.py")
        exit(1)
    
    print("="*60)
    print("WATERMARK EXTRACTION TOOL (with Auto-Recovery)")
    print("="*60)
    
    # Check if target image exists
    if not os.path.exists(WATERMARKED_IMAGE):
        print(f"\n✗ Error: Image file not found: {WATERMARKED_IMAGE}")
        exit(1)
    
    # Check if we can use recovery
    can_use_recovery = (
        ORIGINAL_IMAGE and 
        os.path.exists(ORIGINAL_IMAGE) and
        WATERMARKED_IMAGE != ORIGINAL_IMAGE
    )
    
    print(f"\n📌 Target image: {WATERMARKED_IMAGE}")
    print(f"📌 Watermark length: {WATERMARK_LENGTH}")
    
    # Main extraction strategy: ALWAYS use recovery if original image is available
    if can_use_recovery and ALWAYS_USE_RECOVERY:
        print(f"📌 Original reference: {ORIGINAL_IMAGE}")
        print("\n🔄 Assuming image has been altered (cropped/screenshot/extended)")
        print("🔄 Using recovery-based extraction...")
        
        try:
            extracted_text, recovery_info = extract_with_recovery(
                attacked_img=WATERMARKED_IMAGE,
                original_img=ORIGINAL_IMAGE,
                wm_length=WATERMARK_LENGTH,
                pwd_img=PASSWORD_IMG,
                pwd_wm=PASSWORD_WM,
                scale_range=SCALE_RANGE,
                search_num=SEARCH_NUM
            )
            
            print("\n" + "="*60)
            print("✓ SUCCESS! Watermark extracted after recovery!")
            print("="*60)
            print(f"✓ Extracted text: {extracted_text}")
            print(f"\n📊 Recovery Information:")
            print(f"  - Recovered image saved to: {recovery_info['recovered_file']}")
            print(f"  - Detected crop region: {recovery_info['crop_region']}")
            print(f"  - Scale factor: {recovery_info['scale_factor']:.4f}")
            print(f"  - Match score: {recovery_info['match_score']:.4f}")
            
            # Provide interpretation of the match score
            score = recovery_info['match_score']
            if score > 0.95:
                print(f"  - Quality: Excellent (score > 0.95) ✓")
            elif score > 0.85:
                print(f"  - Quality: Good (score > 0.85) ✓")
            elif score > 0.70:
                print(f"  - Quality: Fair (score > 0.70) ⚠")
            else:
                print(f"  - Quality: Poor (score < 0.70) ⚠ - Extraction may be unreliable")
            
        except Exception as e:
            print(f"\n✗ Recovery-based extraction failed: {e}")
            print("\nPossible reasons:")
            print("  1. The image has been modified too severely (multiple attacks)")
            print("  2. The wrong original image was provided")
            print("  3. WATERMARK_LENGTH doesn't match the embedding")
            print("  4. PASSWORD_IMG and PASSWORD_WM don't match the embedding passwords")
            print("\n💡 Try adjusting recovery settings:")
            print("  - Increase SEARCH_NUM for better accuracy")
            print("  - Adjust SCALE_RANGE if image was heavily resized")
            exit(1)
    
    else:
        # Fallback: Direct extraction (when no original image is available)
        if not can_use_recovery:
            print("\n⚠ No original image provided or same as target image")
            print("⚠ Attempting direct extraction (without recovery)...")
            print("\n💡 For better results with altered images:")
            print("  - Set ORIGINAL_WATERMARKED_IMAGE to your original watermarked image")
            print("  - Make sure it's different from WATERMARKED_IMAGE")
        else:
            print("\n⚠ ALWAYS_USE_RECOVERY is disabled")
            print("⚠ Attempting direct extraction...")
        
        try:
            extracted_text = extract_watermark(WATERMARKED_IMAGE, WATERMARK_LENGTH, PASSWORD_IMG, PASSWORD_WM)
            
            # Check if extraction seems valid
            if extracted_text and len(extracted_text.strip()) > 0:
                print(f"\n✓ SUCCESS! Watermark extracted directly!")
                print(f"✓ Extracted text: {extracted_text}")
            else:
                print(f"\n✗ Direct extraction produced empty/invalid result: '{extracted_text}'")
                print("\n💡 The image may have been altered. Try:")
                print("  1. Set ORIGINAL_WATERMARKED_IMAGE to the original watermarked image")
                print("  2. Set ALWAYS_USE_RECOVERY = True")
                exit(1)
                
        except Exception as e:
            print(f"\n✗ Direct extraction failed: {e}")
            print("\nMake sure:")
            print("  1. The watermarked image exists and is valid")
            print("  2. WATERMARK_LENGTH matches the value from embedding")
            print("  3. PASSWORD_IMG and PASSWORD_WM match the embedding passwords")
            print("\n💡 If the image was cropped/screenshot/altered:")
            print("  - Set ORIGINAL_WATERMARKED_IMAGE to the original watermarked image")
            print("  - Set ALWAYS_USE_RECOVERY = True")
            exit(1)

