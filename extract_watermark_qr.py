#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract and decode a QR code watermark from an image
Includes automatic recovery for cropped/screenshot images
"""
import os
import cv2
import numpy as np
from blind_watermark import WaterMark
from blind_watermark.recover import estimate_crop_parameters, recover_crop
from pyzbar import pyzbar

# Configuration
WATERMARKED_IMAGE = 'examples/output/vd013_background_watermarked_simulated_qr.png'  # Image to extract from
ORIGINAL_IMAGE = 'examples/output/vd013_background_watermarked_qr.webp'  # Original watermarked (for recovery)
WATERMARK_LENGTH = None  # Will be read from qr_code_info.txt
QR_SIZE = None  # QR code dimensions (will be read from qr_code_info.txt)
PASSWORD_IMG = 1
PASSWORD_WM = 1

# Recovery settings
ALWAYS_USE_RECOVERY = True  # Set to True for attacked images
SCALE_RANGE = (0.5, 2)
SEARCH_NUM = 500

def load_qr_info():
    """Load QR code information from saved file"""
    info_file = 'examples/output/qr_code_info.txt'
    
    if not os.path.exists(info_file):
        print(f"⚠ Warning: QR code info file not found: {info_file}")
        print("  Please make sure you ran embed_watermark_qr.py first")
        return None, None, None
    
    qr_size = None
    qr_bits = None
    original_text = None
    
    with open(info_file, 'r') as f:
        for line in f:
            if line.startswith('QR_SIZE='):
                qr_size = int(line.split('=')[1].strip())
            elif line.startswith('QR_BITS='):
                qr_bits = int(line.split('=')[1].strip())
            elif line.startswith('ORIGINAL_TEXT='):
                original_text = line.split('=', 1)[1].strip()
    
    return qr_size, qr_bits, original_text

def bits_to_qr_image(bits, qr_size):
    """
    Convert binary bits back to QR code image
    
    Args:
        bits: Binary bits (numpy array or list)
        qr_size: QR code dimension (modules per side)
    
    Returns:
        QR code as numpy array (2D) with values 0-255
    """
    # Convert bits to numpy array if needed
    bits_array = np.array(bits, dtype=np.uint8)
    
    # Reshape to 2D
    try:
        qr_2d = bits_array.reshape((qr_size, qr_size))
    except ValueError as e:
        print(f"✗ Error reshaping bits to QR code:")
        print(f"  Expected: {qr_size}x{qr_size} = {qr_size*qr_size} bits")
        print(f"  Got: {len(bits_array)} bits")
        raise e
    
    # Convert binary to image: 1 -> black (0), 0 -> white (255)
    qr_img = np.where(qr_2d == 1, 0, 255).astype(np.uint8)
    
    return qr_img

def decode_qr_code(qr_img, save_path=None):
    """
    Decode QR code image to text
    
    Args:
        qr_img: QR code as numpy array
        save_path: Optional path to save QR code image for debugging
    
    Returns:
        Decoded text or None if decoding failed
    """
    # Save QR code for debugging if requested
    if save_path:
        # Scale up for better visualization
        qr_scaled = cv2.resize(qr_img, None, fx=10, fy=10, interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(save_path, qr_scaled)
    
    # Try to decode with pyzbar
    try:
        decoded_objects = pyzbar.decode(qr_img)
        
        if decoded_objects:
            # Get the first decoded object
            decoded_text = decoded_objects[0].data.decode('utf-8')
            return decoded_text
        else:
            # If pyzbar fails, try with scaling
            # QR readers sometimes need minimum size
            for scale in [10, 20, 30, 50]:
                qr_scaled = cv2.resize(qr_img, None, fx=scale, fy=scale, 
                                      interpolation=cv2.INTER_NEAREST)
                decoded_objects = pyzbar.decode(qr_scaled)
                if decoded_objects:
                    decoded_text = decoded_objects[0].data.decode('utf-8')
                    return decoded_text
            
            return None
    except Exception as e:
        print(f"⚠ QR decoding error: {e}")
        return None

def extract_watermark_direct(watermarked_img, wm_length, qr_size, pwd_img=1, pwd_wm=1):
    """
    Extract QR code watermark directly (without recovery)
    
    Args:
        watermarked_img: Path to watermarked image
        wm_length: Length of watermark bits
        qr_size: QR code dimension
        pwd_img: Password for image
        pwd_wm: Password for watermark
    
    Returns:
        Decoded text from QR code
    """
    print("\n[Direct Extraction] Extracting QR watermark...")
    
    # Create WaterMark instance
    bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
    
    # Extract watermark bits
    wm_extract = bwm.extract(watermarked_img, wm_shape=wm_length, mode='bit')
    
    print(f"  - Extracted {len(wm_extract)} bits")
    
    # Convert bits to QR code
    qr_img = bits_to_qr_image(wm_extract, qr_size)
    
    # Save extracted QR for debugging
    output_dir = os.path.dirname(watermarked_img)
    qr_extracted_path = os.path.join(output_dir, 'qr_extracted_direct.png')
    
    # Decode QR code
    decoded_text = decode_qr_code(qr_img, save_path=qr_extracted_path)
    
    if decoded_text:
        print(f"✓ QR code decoded successfully")
        print(f"✓ Extracted QR saved to: {qr_extracted_path}")
    else:
        print(f"✗ QR code decoding failed")
        print(f"⚠ Extracted QR saved to: {qr_extracted_path} (check for corruption)")
    
    return decoded_text

def extract_with_recovery(attacked_img, original_img, wm_length, qr_size,
                         pwd_img=1, pwd_wm=1, scale_range=(0.5, 2), search_num=200):
    """
    Extract QR watermark from attacked image with recovery
    
    Args:
        attacked_img: Path to the modified/attacked image
        original_img: Path to the original watermarked image
        wm_length: Length of the watermark bits
        qr_size: QR code dimension
        pwd_img: Password for image
        pwd_wm: Password for watermark
        scale_range: Scale range for recovery
        search_num: Search iterations
    
    Returns:
        Tuple of (decoded_text, recovery_info)
    """
    print("\n--- Starting Recovery Process ---")
    
    # Load images
    attacked_image = cv2.imread(attacked_img)
    original_image = cv2.imread(original_img)
    
    attacked_h, attacked_w = attacked_image.shape[:2]
    original_h, original_w = original_image.shape[:2]
    
    print(f"Image dimensions:")
    print(f"  - Attacked/Screenshot image: {attacked_w}x{attacked_h}")
    print(f"  - Original watermarked image: {original_w}x{original_h}")
    
    # Determine attack type
    is_extended = (attacked_w >= original_w or attacked_h >= original_h)
    
    if is_extended:
        print(f"\n🔍 Detected: Screenshot/Extended image (larger than original)")
    else:
        print(f"\n🔍 Detected: Cropped image (smaller than original)")
    
    # Estimate parameters
    print("\nEstimating attack parameters...")
    (x1, y1, x2, y2), image_o_shape, score, scale_infer = estimate_crop_parameters(
        original_file=original_img,
        template_file=attacked_img,
        scale=scale_range,
        search_num=search_num
    )
    
    print(f"\nDetected parameters:")
    print(f"  - Crop/Match region: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    print(f"  - Scale factor: {scale_infer}")
    print(f"  - Match score: {score:.4f}")
    
    # Recover image
    base_name = os.path.splitext(attacked_img)[0]
    recovered_file = f"{base_name}_recovered.png"
    print(f"\nRecovering image to: {recovered_file}")
    
    if is_extended:
        cropped_region = attacked_image[y1:y2, x1:x2]
        recovered_image = cv2.resize(cropped_region, (image_o_shape[1], image_o_shape[0]))
        cv2.imwrite(recovered_file, recovered_image)
    else:
        recover_crop(
            template_file=attacked_img,
            output_file_name=recovered_file,
            loc=(x1, y1, x2, y2),
            image_o_shape=image_o_shape
        )
    
    print("Recovery complete!")
    
    # Extract watermark from recovered image
    print("Extracting QR watermark from recovered image...")
    bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
    wm_extract = bwm.extract(recovered_file, wm_shape=wm_length, mode='bit')
    
    print(f"  - Extracted {len(wm_extract)} bits")
    
    # Convert to QR and decode
    qr_img = bits_to_qr_image(wm_extract, qr_size)
    
    # Save extracted QR
    output_dir = os.path.dirname(attacked_img)
    qr_extracted_path = os.path.join(output_dir, 'qr_extracted_recovered.png')
    
    decoded_text = decode_qr_code(qr_img, save_path=qr_extracted_path)
    
    if decoded_text:
        print(f"✓ QR code decoded successfully from recovered image")
        print(f"✓ Extracted QR saved to: {qr_extracted_path}")
    else:
        print(f"✗ QR code decoding failed from recovered image")
        print(f"⚠ Extracted QR saved to: {qr_extracted_path} (check for corruption)")
    
    recovery_info = {
        'crop_region': (x1, y1, x2, y2),
        'scale_factor': scale_infer,
        'match_score': score,
        'recovered_file': recovered_file,
        'qr_image_path': qr_extracted_path
    }
    
    return decoded_text, recovery_info

if __name__ == '__main__':
    print("="*60)
    print("QR CODE WATERMARK EXTRACTION")
    print("="*60)
    
    # Load QR code info
    print("\n[Step 1] Loading QR code information...")
    qr_size_loaded, qr_bits_loaded, original_text = load_qr_info()
    
    if qr_size_loaded is None:
        print("✗ Could not load QR code info. Please run embed_watermark_qr.py first.")
        exit(1)
    
    # Use loaded values if not set
    if WATERMARK_LENGTH is None:
        WATERMARK_LENGTH = qr_bits_loaded
    if QR_SIZE is None:
        QR_SIZE = qr_size_loaded
    
    print(f"✓ QR code info loaded:")
    print(f"  - QR size: {QR_SIZE}x{QR_SIZE}")
    print(f"  - Watermark length: {WATERMARK_LENGTH} bits")
    print(f"  - Original text: {original_text}")
    
    # Check files
    if not os.path.exists(WATERMARKED_IMAGE):
        print(f"\n✗ Error: Watermarked image not found: {WATERMARKED_IMAGE}")
        exit(1)
    
    print(f"\n📌 Target image: {WATERMARKED_IMAGE}")
    print(f"📌 Original reference: {ORIGINAL_IMAGE}")
    
    # Check if recovery is needed
    can_use_recovery = (
        ORIGINAL_IMAGE and
        os.path.exists(ORIGINAL_IMAGE) and
        WATERMARKED_IMAGE != ORIGINAL_IMAGE
    )
    
    # Main extraction
    if can_use_recovery and ALWAYS_USE_RECOVERY:
        print("\n🔄 Using recovery-based extraction...")
        
        try:
            decoded_text, recovery_info = extract_with_recovery(
                attacked_img=WATERMARKED_IMAGE,
                original_img=ORIGINAL_IMAGE,
                wm_length=WATERMARK_LENGTH,
                qr_size=QR_SIZE,
                pwd_img=PASSWORD_IMG,
                pwd_wm=PASSWORD_WM,
                scale_range=SCALE_RANGE,
                search_num=SEARCH_NUM
            )
            
            print("\n" + "="*60)
            if decoded_text:
                print("✓ SUCCESS! QR CODE DECODED!")
                print("="*60)
                print(f"✓ Extracted text: {decoded_text}")
                print(f"\n📊 Recovery Information:")
                print(f"  - Match score: {recovery_info['match_score']:.4f}")
                print(f"  - Scale factor: {recovery_info['scale_factor']:.4f}")
                print(f"  - Recovered image: {recovery_info['recovered_file']}")
                print(f"  - QR code image: {recovery_info['qr_image_path']}")
                
                if original_text and decoded_text == original_text:
                    print(f"\n✓ VERIFIED: Extracted text matches original!")
                elif original_text:
                    print(f"\n⚠ WARNING: Text differs from original")
                    print(f"  Expected: {original_text}")
                    print(f"  Got: {decoded_text}")
                    
                    # Show character-by-character comparison
                    print(f"\n  Character comparison:")
                    max_len = max(len(original_text), len(decoded_text))
                    for i in range(max_len):
                        orig_char = original_text[i] if i < len(original_text) else '∅'
                        dec_char = decoded_text[i] if i < len(decoded_text) else '∅'
                        match = '✓' if orig_char == dec_char else '✗'
                        print(f"    {i:3d}: '{orig_char}' vs '{dec_char}' {match}")
            else:
                print("✗ FAILED: QR CODE COULD NOT BE DECODED")
                print("="*60)
                print(f"⚠ QR code was extracted but decoding failed")
                print(f"  - Match score: {recovery_info['match_score']:.4f}")
                print(f"  - QR image saved to: {recovery_info['qr_image_path']}")
                print(f"\nPossible reasons:")
                print(f"  1. Too much degradation (match score < 0.85)")
                print(f"  2. QR code corruption beyond error correction capacity")
                print(f"  3. Incorrect recovery parameters")
                
        except Exception as e:
            print(f"\n✗ Recovery-based extraction failed: {e}")
            import traceback
            traceback.print_exc()
            exit(1)
    
    else:
        # Direct extraction
        print("\n⚠ Attempting direct extraction (no recovery)...")
        
        try:
            decoded_text = extract_watermark_direct(
                WATERMARKED_IMAGE,
                WATERMARK_LENGTH,
                QR_SIZE,
                PASSWORD_IMG,
                PASSWORD_WM
            )
            
            print("\n" + "="*60)
            if decoded_text:
                print("✓ SUCCESS! QR CODE DECODED!")
                print("="*60)
                print(f"✓ Extracted text: {decoded_text}")
                
                if original_text and decoded_text == original_text:
                    print(f"✓ VERIFIED: Matches original text!")
                elif original_text:
                    print(f"⚠ WARNING: Differs from original: {original_text}")
            else:
                print("✗ FAILED: QR CODE COULD NOT BE DECODED")
                print("="*60)
                
        except Exception as e:
            print(f"\n✗ Direct extraction failed: {e}")
            import traceback
            traceback.print_exc()
            exit(1)

