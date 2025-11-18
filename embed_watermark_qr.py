#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embed a QR code as a watermark in an image
Uses QR code's built-in error correction for improved resilience
"""
import os
import cv2
import numpy as np
import qrcode
from blind_watermark import WaterMark

# Configuration
INPUT_IMAGE = 'examples/pic/vd013_background.webp'
OUTPUT_IMAGE = 'examples/output/vd013_background_watermarked_qr.webp'
WATERMARK_TEXT = '5.34.3+53403000(tags/release-5.34.3-29751)'
PASSWORD_IMG = 1
PASSWORD_WM = 1

# QR Code settings
QR_ERROR_CORRECTION = qrcode.constants.ERROR_CORRECT_H  # Highest (30% error correction)
# Options: ERROR_CORRECT_L (7%), ERROR_CORRECT_M (15%), ERROR_CORRECT_Q (25%), ERROR_CORRECT_H (30%)

def text_to_qr_bits(text, error_correction=qrcode.constants.ERROR_CORRECT_H):
    """
    Convert text to QR code and then to binary bits
    
    Args:
        text: Text to encode in QR code
        error_correction: QR error correction level
            - ERROR_CORRECT_L: 7% error correction
            - ERROR_CORRECT_M: 15% error correction
            - ERROR_CORRECT_Q: 25% error correction
            - ERROR_CORRECT_H: 30% error correction (recommended)
    
    Returns:
        numpy array of bits (0s and 1s)
    """
    print(f"Generating QR code for text: {text}")
    
    # Create QR code
    qr = qrcode.QRCode(
        version=None,  # Auto-detect version based on data
        error_correction=error_correction,
        box_size=1,  # 1 pixel per module
        border=0,  # No border (we'll add padding if needed)
    )
    
    qr.add_data(text)
    qr.make(fit=True)
    
    # Get QR code as image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to numpy array
    # PIL QR code is in mode '1' (binary), so convert to 'L' (grayscale) first
    qr_img_gray = qr_img.convert('L')
    qr_array = np.array(qr_img_gray)
    
    # Convert to binary (0 and 1)
    # White (255) -> 0, Black (0) -> 1
    qr_binary = (qr_array < 128).astype(np.uint8)
    
    # Flatten to 1D array
    qr_bits = qr_binary.flatten()
    
    print(f"QR Code generated:")
    print(f"  - Version: {qr.version}")
    print(f"  - Size: {qr_array.shape[0]}x{qr_array.shape[1]} modules")
    print(f"  - Total bits: {len(qr_bits)}")
    print(f"  - Error correction: {_get_error_correction_name(error_correction)}")
    
    # Save QR code visualization for reference
    output_dir = os.path.dirname(OUTPUT_IMAGE)
    qr_visual_path = os.path.join(output_dir, 'qr_code_visual.png')
    
    # Convert binary (0/1) to grayscale (0/255) for proper visualization
    # 0 -> 255 (white), 1 -> 0 (black)
    qr_display = np.where(qr_binary.reshape(qr_array.shape), 0, 255).astype(np.uint8)
    
    # Scale up QR code for visualization (10x)
    qr_visual = cv2.resize(qr_display, None, fx=10, fy=10, interpolation=cv2.INTER_NEAREST)
    cv2.imwrite(qr_visual_path, qr_visual)
    print(f"  - QR code visual saved to: {qr_visual_path}")
    
    # Save QR code dimensions for extraction
    qr_info_path = os.path.join(output_dir, 'qr_code_info.txt')
    with open(qr_info_path, 'w') as f:
        f.write(f"QR_SIZE={qr_array.shape[0]}\n")
        f.write(f"QR_BITS={len(qr_bits)}\n")
        f.write(f"QR_VERSION={qr.version}\n")
        f.write(f"ERROR_CORRECTION={_get_error_correction_name(error_correction)}\n")
        f.write(f"ORIGINAL_TEXT={text}\n")
    print(f"  - QR code info saved to: {qr_info_path}")
    
    return qr_bits, qr_array.shape[0]

def _get_error_correction_name(level):
    """Get human-readable name for error correction level"""
    names = {
        qrcode.constants.ERROR_CORRECT_L: "L (7% recovery)",
        qrcode.constants.ERROR_CORRECT_M: "M (15% recovery)",
        qrcode.constants.ERROR_CORRECT_Q: "Q (25% recovery)",
        qrcode.constants.ERROR_CORRECT_H: "H (30% recovery)",
    }
    return names.get(level, "Unknown")

def embed_qr_watermark(input_img, output_img, qr_bits, pwd_img=1, pwd_wm=1):
    """
    Embed QR code bits as watermark in image
    
    Args:
        input_img: Path to input image
        output_img: Path to save watermarked image
        qr_bits: QR code as binary bits (numpy array)
        pwd_img: Password for image
        pwd_wm: Password for watermark
    
    Returns:
        Length of embedded watermark
    """
    print("\n" + "="*60)
    print("EMBEDDING QR CODE WATERMARK")
    print("="*60)
    
    # Check if input image exists
    if not os.path.exists(input_img):
        raise FileNotFoundError(f"Input image not found: {input_img}")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_img), exist_ok=True)
    
    # Create WaterMark instance
    bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
    
    # Read the input image
    print(f"\nReading input image: {input_img}")
    bwm.read_img(input_img)
    
    img = cv2.imread(input_img)
    h, w = img.shape[:2]
    print(f"Image dimensions: {w}x{h}")
    
    # Embed QR code bits as watermark
    print(f"\nEmbedding QR code watermark...")
    print(f"  - QR code bits: {len(qr_bits)}")
    print(f"  - Passwords: IMG={pwd_img}, WM={pwd_wm}")
    
    # Set the watermark bits directly through the core object
    # The library needs wm_bit in the core, not the outer wrapper
    bwm.wm_bit = qr_bits
    bwm.bwm_core.wm_bit = qr_bits
    bwm.bwm_core.wm_size = len(qr_bits)
    
    # Embed the watermark
    bwm.embed(output_img)
    
    wm_length = len(bwm.wm_bit)
    
    print(f"\n✓ Watermark embedded successfully!")
    print(f"✓ Watermarked image saved to: {output_img}")
    print(f"\n📊 Watermark Information:")
    print(f"  - Watermark length: {wm_length} bits")
    print(f"  - Password IMG: {pwd_img}")
    print(f"  - Password WM: {pwd_wm}")
    
    print(f"\n💾 IMPORTANT - Save these values for extraction:")
    print(f"  WATERMARK_LENGTH = {wm_length}")
    print(f"  PASSWORD_IMG = {pwd_img}")
    print(f"  PASSWORD_WM = {pwd_wm}")
    print(f"  QR_SIZE = (saved in qr_code_info.txt)")
    
    return wm_length

if __name__ == '__main__':
    try:
        print("="*60)
        print("QR CODE WATERMARK EMBEDDING")
        print("="*60)
        print(f"\nConfiguration:")
        print(f"  Input image: {INPUT_IMAGE}")
        print(f"  Output image: {OUTPUT_IMAGE}")
        print(f"  Watermark text: {WATERMARK_TEXT}")
        print(f"  QR Error Correction: {_get_error_correction_name(QR_ERROR_CORRECTION)}")
        
        # Step 1: Convert text to QR code bits
        print(f"\n[Step 1] Converting text to QR code...")
        qr_bits, qr_size = text_to_qr_bits(WATERMARK_TEXT, QR_ERROR_CORRECTION)
        
        # Step 2: Embed QR code as watermark
        print(f"\n[Step 2] Embedding QR code in image...")
        wm_length = embed_qr_watermark(
            input_img=INPUT_IMAGE,
            output_img=OUTPUT_IMAGE,
            qr_bits=qr_bits,
            pwd_img=PASSWORD_IMG,
            pwd_wm=PASSWORD_WM
        )
        
        # Summary
        print("\n" + "="*60)
        print("✓ QR CODE WATERMARK EMBEDDING COMPLETE!")
        print("="*60)
        print(f"\n📋 Summary:")
        print(f"  - Original text: {WATERMARK_TEXT}")
        print(f"  - QR code size: {qr_size}x{qr_size} modules")
        print(f"  - Total bits: {wm_length}")
        print(f"  - Error correction: {_get_error_correction_name(QR_ERROR_CORRECTION)}")
        print(f"  - Watermarked image: {OUTPUT_IMAGE}")
        
        print(f"\n🔍 QR Code Advantages:")
        print(f"  ✓ Built-in error correction (30% damage recovery)")
        print(f"  ✓ Structured format with positioning patterns")
        print(f"  ✓ Can recover from partial corruption")
        
        print(f"\n➡️  Next Step:")
        print(f"  Use extract_watermark_qr.py to extract and decode the QR watermark")
        print(f"  WATERMARK_LENGTH = {wm_length}")
        
    except Exception as e:
        print(f"\n✗ Error during embedding: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

