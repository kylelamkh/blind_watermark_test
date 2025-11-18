#!/usr/bin/env python3
"""
Test watermark extraction with PROPER recovery workflow
(like the example_str.py demonstrates)
"""
import cv2
import os
from blind_watermark import WaterMark, att
from blind_watermark.recover import estimate_crop_parameters, recover_crop

print("="*70)
print("TESTING WITH PROPER RECOVERY WORKFLOW")
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
ori_img_shape = (h, w)

print(f"\nOriginal watermarked image: {w}x{h}")
print(f"Testing crop+resize attacks WITH recovery...\n")

# Test cases with recovery
tests = [
    {
        'name': 'Test 1: Crop to 80% + Resize to 93% (like your screenshot)',
        'attack_file': os.path.join(output_dir, 'attack_crop80_scale93.png'),
        'recovered_file': os.path.join(output_dir, 'attack_crop80_scale93_recovered.png'),
        'loc_r': ((0.1, 0.1), (0.9, 0.9)),
        'scale': 0.93
    },
    {
        'name': 'Test 2: Crop to 70% + Resize to 70% (like example)',
        'attack_file': os.path.join(output_dir, 'attack_crop70_scale70.png'),
        'recovered_file': os.path.join(output_dir, 'attack_crop70_scale70_recovered.png'),
        'loc_r': ((0.1, 0.1), (0.7, 0.6)),
        'scale': 0.7
    },
    {
        'name': 'Test 3: Small crop + Resize to 95%',
        'attack_file': os.path.join(output_dir, 'attack_crop95_scale95.png'),
        'recovered_file': os.path.join(output_dir, 'attack_crop95_scale95_recovered.png'),
        'loc_r': ((0.05, 0.05), (0.95, 0.95)),
        'scale': 0.95
    },
]

results = []

for test in tests:
    print(f"\n{test['name']}")
    print("-" * 70)
    
    try:
        # Calculate actual crop coordinates
        loc_r = test['loc_r']
        scale = test['scale']
        x1, y1, x2, y2 = int(w * loc_r[0][0]), int(h * loc_r[0][1]), int(w * loc_r[1][0]), int(h * loc_r[1][1])
        
        print(f"1. Applying attack: crop ({x1},{y1}) to ({x2},{y2}), scale {scale}")
        
        # Apply crop + resize attack
        att.cut_att3(input_filename=watermarked_img, 
                    output_file_name=test['attack_file'],
                    loc=(x1, y1, x2, y2), 
                    scale=scale)
        
        attacked_img = cv2.imread(test['attack_file'])
        print(f"   Attacked image size: {attacked_img.shape[1]}x{attacked_img.shape[0]}")
        
        # Estimate parameters (simulating not knowing the attack params)
        print(f"2. Estimating attack parameters...")
        (x1_est, y1_est, x2_est, y2_est), image_o_shape, score, scale_infer = estimate_crop_parameters(
            original_file=watermarked_img,
            template_file=test['attack_file'],
            scale=(0.5, 2),
            search_num=200
        )
        
        print(f"   Estimated: crop ({x1_est},{y1_est}) to ({x2_est},{y2_est})")
        print(f"   Estimated scale: {scale_infer:.4f} (actual: {scale})")
        print(f"   Match score: {score:.4f}")
        
        if score < 0.5:
            print(f"   ⚠ WARNING: Low match score!")
        
        # Recover the image to original dimensions
        print(f"3. Recovering image to original dimensions...")
        recover_crop(
            template_file=test['attack_file'],
            output_file_name=test['recovered_file'],
            loc=(x1_est, y1_est, x2_est, y2_est),
            image_o_shape=image_o_shape
        )
        
        recovered_img = cv2.imread(test['recovered_file'])
        print(f"   Recovered image size: {recovered_img.shape[1]}x{recovered_img.shape[0]}")
        
        # Extract watermark from recovered image
        print(f"4. Extracting watermark from recovered image...")
        bwm = WaterMark(password_img=pwd_img, password_wm=pwd_wm)
        wm_extract = bwm.extract(test['recovered_file'], wm_shape=wm_length, mode='str')
        
        expected = '5.34.3+53403000(tags/release-5.34.3-29751)'
        if wm_extract == expected:
            print(f"   ✓ SUCCESS! Extracted: {wm_extract}")
            results.append((test['name'], True, wm_extract, score))
        else:
            print(f"   ⚠ PARTIAL: {wm_extract}")
            results.append((test['name'], 'partial', wm_extract, score))
            
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        results.append((test['name'], False, str(e), 0.0))

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

success_count = sum(1 for r in results if r[1] is True)
total_count = len(results)

print(f"\nPassed: {success_count}/{total_count} tests\n")

for name, status, details, score in results:
    if status is True:
        print(f"✓ {name}")
        print(f"  Match score: {score:.4f}")
    elif status == 'partial':
        print(f"⚠ {name}")
        print(f"  Extracted: {details[:60]}...")
        print(f"  Match score: {score:.4f}")
    else:
        print(f"✗ {name}")
        print(f"  Error: {details[:60]}...")

print("\n" + "="*70)
if success_count == total_count:
    print("✓ All tests passed with proper recovery workflow!")
    print("  The watermark CAN survive crop+resize if properly recovered.")
elif success_count > 0:
    print("⚠ Some tests passed - recovery works for certain parameters.")
else:
    print("✗ Recovery workflow failed for all tests.")
    print("  This suggests the screenshot degradation is too severe.")
print("="*70)

