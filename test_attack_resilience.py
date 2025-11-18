#!/usr/bin/env python3
"""
Test what attacks the watermark can survive
This helps understand the limitations for screenshot-based extraction
"""
import cv2
import os
from blind_watermark import WaterMark, att

print("="*70)
print("TESTING WATERMARK ATTACK RESILIENCE")
print("="*70)

# Configuration
watermarked_img = 'examples/output/vd013_background_watermarked.webp'
wm_length = 334
pwd_img = 1
pwd_wm = 1

output_dir = 'examples/output'

# Load the watermarked image
img = cv2.imread(watermarked_img)
h, w = img.shape[:2]

print(f"\nOriginal watermarked image: {w}x{h}")
print(f"Testing various attacks...\n")

# Test cases
tests = [
    {
        'name': '1. No attack (baseline)',
        'file': os.path.join(output_dir, 'attack_test_none.png'),
        'apply': lambda img: img
    },
    {
        'name': '2. Format conversion only (WEBP→PNG)',
        'file': os.path.join(output_dir, 'attack_test_format.png'),
        'apply': lambda img: img  # Just save as PNG
    },
    {
        'name': '3. Crop 80% (no resize)',
        'file': os.path.join(output_dir, 'attack_test_crop.png'),
        'apply': lambda img: att.cut_att3(input_img=img, loc=(int(w*0.1), int(h*0.1), int(w*0.9), int(h*0.9)), scale=None, output_file_name=None)
    },
    {
        'name': '4. Resize to 95% (no crop)',
        'file': os.path.join(output_dir, 'attack_test_resize95.png'),
        'apply': lambda img: cv2.resize(img, (int(w*0.95), int(h*0.95)))
    },
    {
        'name': '5. Resize to 90% (no crop)',
        'file': os.path.join(output_dir, 'attack_test_resize90.png'),
        'apply': lambda img: cv2.resize(img, (int(w*0.90), int(h*0.90)))
    },
    {
        'name': '6. Crop + Resize (like screenshot)',
        'file': os.path.join(output_dir, 'attack_test_crop_resize.png'),
        'apply': lambda img: att.cut_att3(input_img=img, loc=(int(w*0.05), int(h*0.05), int(w*0.95), int(h*0.95)), scale=0.93, output_file_name=None)
    },
]

results = []

for test in tests:
    print(f"{test['name']}...")
    
    try:
        # Apply the attack
        attacked_img = test['apply'](img.copy())
        cv2.imwrite(test['file'], attacked_img)
        
        # Try to extract
        bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
        wm_extract = bwm.extract(test['file'], wm_shape=wm_length, mode='str')
        
        if wm_extract == '5.34.3+53403000(tags/release-5.34.3-29751)':
            result = "✓ SUCCESS"
            results.append((test['name'], True, wm_extract))
        else:
            result = f"⚠ PARTIAL (got: {wm_extract})"
            results.append((test['name'], 'partial', wm_extract))
            
        print(f"  {result}")
        
    except Exception as e:
        result = f"✗ FAILED ({str(e)[:50]}...)"
        results.append((test['name'], False, str(e)))
        print(f"  {result}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

success_count = sum(1 for r in results if r[1] is True)
total_count = len(results)

print(f"\nPassed: {success_count}/{total_count} tests\n")

for name, status, details in results:
    if status is True:
        print(f"✓ {name}")
    elif status == 'partial':
        print(f"⚠ {name} - Extracted: {details}")
    else:
        print(f"✗ {name} - {details[:60]}")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if success_count == total_count:
    print("✓ Watermark is very robust!")
elif success_count >= 3:
    print("⚠ Watermark survives some attacks but not all.")
    print("  Your screenshot process might be too aggressive.")
else:
    print("✗ Watermark is fragile and doesn't survive most attacks.")
    print("  Consider:")
    print("  1. Using a stronger watermark strength when embedding")
    print("  2. Avoiding resize/scale operations")
    print("  3. Keeping original image format (WEBP)")
    print("  4. Using a different watermarking technique for screenshots")

print("\nFailed tests indicate operations that destroy the watermark.")
print("If 'Crop + Resize' fails, screenshot-based extraction won't work.")
print("="*70)

