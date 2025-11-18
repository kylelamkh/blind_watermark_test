#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to embed a string watermark into an image
"""
import os
from blind_watermark import WaterMark

# Configuration
INPUT_IMAGE = 'examples/pic/vd013_background.webp'  # Path to your original image
WATERMARK_TEXT = '5.34.3+53403000(tags/release-5.34.3-29751)'  # Your watermark string
PASSWORD_IMG = 1  # Password for image (can be any number)
PASSWORD_WM = 1   # Password for watermark (can be any number)

def embed_watermark(input_img, output_img, watermark_text, pwd_img=1, pwd_wm=1):
    """
    Embed a string watermark into an image
    
    Args:
        input_img: Path to the input image
        output_img: Path to save the watermarked image
        watermark_text: The string to embed as watermark
        pwd_img: Password for image embedding
        pwd_wm: Password for watermark
    
    Returns:
        Length of watermark bits (needed for extraction)
    """
    # Create WaterMark instance
    bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
    
    # Read the original image
    bwm.read_img(input_img)
    
    # Read the watermark text
    bwm.read_wm(watermark_text, mode='str')
    
    # Embed the watermark and save
    bwm.embed(output_img)
    
    # Get the length of watermark bits (needed for extraction)
    len_wm = len(bwm.wm_bit)
    
    return len_wm

if __name__ == '__main__':
    # Generate output path by adding _watermarked suffix
    input_dir = os.path.dirname(INPUT_IMAGE)
    input_filename = os.path.basename(INPUT_IMAGE)
    input_name, input_ext = os.path.splitext(input_filename)
    
    # Create output in examples/output/ directory with _watermarked suffix
    output_dir = 'examples/output'
    output_image = os.path.join(output_dir, f'{input_name}_watermarked.webp')
    
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Embed the watermark
    print(f"Embedding watermark into: {INPUT_IMAGE}")
    print(f"Watermark text: {WATERMARK_TEXT}")
    
    len_wm = embed_watermark(INPUT_IMAGE, output_image, WATERMARK_TEXT, PASSWORD_IMG, PASSWORD_WM)
    
    print(f"✓ Watermark embedded successfully!")
    print(f"✓ Output saved to: {output_image}")
    print(f"✓ Watermark length: {len_wm}")
    print(f"\nIMPORTANT: Save this information for extraction:")
    print(f"  - Watermark length: {len_wm}")
    print(f"  - Password IMG: {PASSWORD_IMG}")
    print(f"  - Password WM: {PASSWORD_WM}")

