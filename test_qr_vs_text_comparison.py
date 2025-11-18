#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare QR Code vs Text watermarking performance
Tests both approaches against various attacks to see if QR error correction helps
"""
import os
import cv2
import numpy as np
from blind_watermark import WaterMark, att
from blind_watermark.recover import estimate_crop_parameters, recover_crop
import qrcode

def text_to_qr_bits(text):
    """Convert text to QR code bits"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% error correction
        box_size=1,
        border=0,
    )
    qr.add_data(text)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    # Convert to grayscale first (PIL mode '1' to 'L')
    qr_img_gray = qr_img.convert('L')
    qr_array = np.array(qr_img_gray)
    # Black pixels (< 128) -> 1, White pixels (>= 128) -> 0
    qr_binary = (qr_array < 128).astype(np.uint8)
    qr_bits = qr_binary.flatten()
    return qr_bits, qr_array.shape[0]

def bits_to_qr_image(bits, qr_size):
    """Convert bits back to QR code image"""
    bits_array = np.array(bits, dtype=np.uint8)
    qr_2d = bits_array.reshape((qr_size, qr_size))
    # 1 -> black (0), 0 -> white (255)
    qr_img = np.where(qr_2d == 1, 0, 255).astype(np.uint8)
    return qr_img

def decode_qr_code(qr_img):
    """Decode QR code to text"""
    try:
        from pyzbar import pyzbar
        # Try different scales
        for scale in [1, 10, 20, 30]:
            if scale > 1:
                qr_scaled = cv2.resize(qr_img, None, fx=scale, fy=scale, 
                                      interpolation=cv2.INTER_NEAREST)
            else:
                qr_scaled = qr_img
            decoded_objects = pyzbar.decode(qr_scaled)
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        return None
    except Exception as e:
        return None

def test_watermark_type(wm_type, test_name, input_img, watermark_text, 
                        crop_percent, resize_percent):
    """
    Test a single watermark type against an attack
    
    Returns: (success, extracted_text, match_score, details)
    """
    print(f"\n{'='*70}")
    print(f"Testing: {wm_type} - {test_name}")
    print(f"{'='*70}")
    
    output_dir = 'examples/output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Paths
    watermarked_file = f'{output_dir}/test_{wm_type}_watermarked.png'
    attacked_file = f'{output_dir}/test_{wm_type}_attacked.png'
    recovered_file = f'{output_dir}/test_{wm_type}_recovered.png'
    
    try:
        # Step 1: Embed watermark
        print(f"\n[1] Embedding {wm_type} watermark...")
        bwm = WaterMark(password_img=1, password_wm=1)
        bwm.read_img(input_img)
        
        if wm_type == 'TEXT':
            bwm.read_wm(watermark_text, mode='str')
            wm_length = len(bwm.wm_bit)
        else:  # QR
            qr_bits, qr_size = text_to_qr_bits(watermark_text)
            bwm.wm_bit = qr_bits
            bwm.bwm_core.wm_bit = qr_bits
            bwm.bwm_core.wm_size = len(qr_bits)
            wm_length = len(qr_bits)
        
        bwm.embed(watermarked_file)
        print(f"  ✓ Watermark embedded ({wm_length} bits)")
        
        # Step 2: Apply attack
        print(f"\n[2] Applying attack (crop {crop_percent}%, resize {resize_percent}%)...")
        img = cv2.imread(watermarked_file)
        h, w = img.shape[:2]
        
        # Calculate crop
        margin_x = int(w * (1 - crop_percent / 100) / 2)
        margin_y = int(h * (1 - crop_percent / 100) / 2)
        x1, y1 = margin_x, margin_y
        x2, y2 = w - margin_x, h - margin_y
        
        # Apply crop + resize
        scale = resize_percent / 100
        att.cut_att3(input_filename=watermarked_file, 
                    output_file_name=attacked_file,
                    loc=(x1, y1, x2, y2), 
                    scale=scale)
        
        attacked_img = cv2.imread(attacked_file)
        print(f"  ✓ Attacked image: {attacked_img.shape[1]}x{attacked_img.shape[0]}")
        
        # Step 3: Recover
        print(f"\n[3] Estimating parameters and recovering...")
        (x1_est, y1_est, x2_est, y2_est), image_o_shape, score, scale_infer = estimate_crop_parameters(
            original_file=watermarked_file,
            template_file=attacked_file,
            scale=(0.5, 2),
            search_num=500
        )
        print(f"  - Match score: {score:.4f}")
        
        recover_crop(
            template_file=attacked_file,
            output_file_name=recovered_file,
            loc=(x1_est, y1_est, x2_est, y2_est),
            image_o_shape=image_o_shape
        )
        print(f"  ✓ Image recovered")
        
        # Step 4: Extract
        print(f"\n[4] Extracting watermark...")
        bwm_extract = WaterMark(password_img=1, password_wm=1)
        
        if wm_type == 'TEXT':
            extracted = bwm_extract.extract(recovered_file, wm_shape=wm_length, mode='str')
            success = (extracted == watermark_text)
            print(f"  - Extracted: {extracted}")
        else:  # QR
            wm_bits = bwm_extract.extract(recovered_file, wm_shape=wm_length, mode='bit')
            qr_img = bits_to_qr_image(wm_bits, qr_size)
            
            # Save QR for inspection
            qr_save_path = f'{output_dir}/test_{wm_type}_extracted_qr.png'
            qr_visual = cv2.resize(qr_img, None, fx=10, fy=10, interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(qr_save_path, qr_visual)
            
            extracted = decode_qr_code(qr_img)
            success = (extracted == watermark_text) if extracted else False
            print(f"  - Extracted: {extracted if extracted else 'DECODE FAILED'}")
            print(f"  - QR saved to: {qr_save_path}")
        
        # Step 5: Analyze
        if success:
            print(f"\n✓ SUCCESS: {wm_type} watermark extracted perfectly!")
            status = "✓ SUCCESS"
        elif extracted and wm_type == 'TEXT':
            # Check if partially correct
            correct_chars = sum(1 for a, b in zip(extracted, watermark_text) if a == b)
            accuracy = correct_chars / len(watermark_text)
            print(f"\n⚠ PARTIAL: {wm_type} watermark partially extracted ({accuracy*100:.1f}% accuracy)")
            status = f"⚠ PARTIAL ({accuracy*100:.0f}%)"
        else:
            print(f"\n✗ FAILED: {wm_type} watermark extraction failed")
            status = "✗ FAILED"
        
        return {
            'success': success,
            'status': status,
            'extracted': extracted,
            'match_score': score,
            'wm_length': wm_length
        }
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'status': '✗ ERROR',
            'extracted': None,
            'match_score': 0,
            'wm_length': 0
        }

def run_comparison_tests():
    """Run comprehensive comparison between TEXT and QR watermarking"""
    
    print("="*70)
    print("QR CODE vs TEXT WATERMARKING COMPARISON")
    print("="*70)
    print("\nTesting hypothesis: QR code error correction improves resilience")
    print("against attacks that cause partial watermark corruption")
    
    input_image = 'examples/pic/vd013_background.webp'
    watermark_text = '5.34.3+53403000(tags/release-5.34.3-29751)'
    
    # Test scenarios: (name, crop_percent, resize_percent)
    scenarios = [
        ("Mild Attack", 95, 95),
        ("Moderate Attack", 80, 93),
        ("Aggressive Attack", 70, 70),
    ]
    
    results = []
    
    for test_name, crop_pct, resize_pct in scenarios:
        print(f"\n\n{'#'*70}")
        print(f"# SCENARIO: {test_name} (Crop {crop_pct}% + Resize {resize_pct}%)")
        print(f"{'#'*70}")
        
        # Test TEXT
        text_result = test_watermark_type(
            'TEXT', test_name, input_image, watermark_text, crop_pct, resize_pct
        )
        
        # Test QR
        qr_result = test_watermark_type(
            'QR', test_name, input_image, watermark_text, crop_pct, resize_pct
        )
        
        results.append({
            'scenario': test_name,
            'crop': crop_pct,
            'resize': resize_pct,
            'text': text_result,
            'qr': qr_result
        })
    
    # Print summary
    print("\n\n")
    print("="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    
    print(f"\n{'Scenario':<20} | {'TEXT Result':<20} | {'QR Result':<20} | {'Winner':<10}")
    print("-" * 80)
    
    text_wins = 0
    qr_wins = 0
    ties = 0
    
    for r in results:
        text_status = r['text']['status']
        qr_status = r['qr']['status']
        
        # Determine winner
        text_success = r['text']['success']
        qr_success = r['qr']['success']
        
        if text_success and qr_success:
            winner = "TIE"
            ties += 1
        elif text_success:
            winner = "TEXT"
            text_wins += 1
        elif qr_success:
            winner = "QR ⭐"
            qr_wins += 1
        elif r['text']['match_score'] > r['qr']['match_score']:
            winner = "TEXT (better)"
            text_wins += 1
        elif r['qr']['match_score'] > r['text']['match_score']:
            winner = "QR (better)"
            qr_wins += 1
        else:
            winner = "TIE"
            ties += 1
        
        print(f"{r['scenario']:<20} | {text_status:<20} | {qr_status:<20} | {winner:<10}")
        print(f"{'  Match scores:':<20} | {r['text']['match_score']:<20.4f} | {r['qr']['match_score']:<20.4f} |")
        print("-" * 80)
    
    # Final verdict
    print(f"\n{'='*70}")
    print("FINAL VERDICT")
    print(f"{'='*70}")
    print(f"\nScore: TEXT {text_wins} - {qr_wins} QR (Ties: {ties})")
    
    if qr_wins > text_wins:
        print(f"\n🏆 QR CODE WINS!")
        print("   QR code error correction provides measurable improvement")
    elif text_wins > qr_wins:
        print(f"\n🏆 TEXT WINS!")
        print("   No significant benefit from QR code error correction")
    else:
        print(f"\n🤝 TIE!")
        print("   Both approaches perform similarly")
    
    print(f"\n📊 Detailed Analysis:")
    print(f"  - TEXT watermark: {sum(1 for r in results if r['text']['success'])}/{len(results)} full success")
    print(f"  - QR watermark:   {sum(1 for r in results if r['qr']['success'])}/{len(results)} full success")
    print(f"  - TEXT avg match score: {np.mean([r['text']['match_score'] for r in results]):.4f}")
    print(f"  - QR avg match score:   {np.mean([r['qr']['match_score'] for r in results]):.4f}")
    
    # Size comparison
    text_size = results[0]['text']['wm_length']
    qr_size = results[0]['qr']['wm_length']
    print(f"\n📏 Watermark Size:")
    print(f"  - TEXT: {text_size} bits")
    print(f"  - QR:   {qr_size} bits ({qr_size/text_size:.1f}x larger)")
    
    print(f"\n💡 Conclusion:")
    if qr_wins > text_wins:
        print("  QR code's error correction DOES help with programmatic attacks")
        print("  The 30% error correction capacity successfully recovers from")
        print("  partial watermark corruption that TEXT watermarks cannot handle.")
    else:
        print("  QR code's error correction does NOT provide significant benefit")
        print("  for these attack scenarios. The watermark either survives well")
        print("  enough for TEXT extraction or is too corrupted for even QR recovery.")
    
    return results

if __name__ == '__main__':
    try:
        results = run_comparison_tests()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

