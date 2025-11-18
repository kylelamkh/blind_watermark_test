# QR Code Watermarking Test - Quick Summary

## ❓ Question
**Does QR code's 30% error correction help watermarks survive screenshot attacks better than plain text watermarks?**

---

## ✅ Answer
**NO** ❌ - QR codes provide **no advantage** over text watermarks for screenshot attacks.

---

## 📊 Test Results

| Metric | TEXT Watermark | QR Code Watermark |
|--------|----------------|-------------------|
| **Match Score** | 0.8018 | 0.7899 ⬇️ |
| **PSNR** | 11.24 dB | ~11 dB |
| **Extraction** | ❌ FAILED | ❌ FAILED |
| **Watermark Size** | 334 bits | 1369 bits (4.1x larger) |
| **Complexity** | Simple | Complex (QR encode/decode) |

**Winner:** TEXT (smaller, simpler, same effectiveness)

---

## 🔍 Visual Evidence

### Original QR Code (Embedded)
![Original](examples/output/qr_code_visual.png)

**Status:** ✅ Perfect, scannable

### Extracted QR Code (From Screenshot)
![Extracted](examples/output/qr_extracted_recovered.png)

**Status:** ❌ Completely corrupted (>70% damage, exceeds 30% error correction capacity)

---

## 🎯 Why QR Code Failed

```
QR Error Correction Works on DATA, not IMAGE DEGRADATION

Screenshot Pipeline:
┌──────────────────────────────────────────────┐
│ Watermarked Image (QR bits in DCT)          │
│         ↓                                     │
│ Display Rendering (color conversion)         │
│         ↓                                     │
│ Screenshot Tool (compression)                 │
│         ↓                                     │
│ Format Change (WebP → PNG)                   │
│         ↓                                     │
│ RESULT: PSNR 11 dB (severe degradation)     │
│         ↓                                     │
│ DCT Extraction: ✗ FAILS (corrupted bits)    │
│         ↓                                     │
│ QR Decoding: ✗ NEVER REACHED                │
│   (Error correction has nothing to work on)  │
└──────────────────────────────────────────────┘
```

**Key Insight:** QR error correction operates AFTER bit extraction, but screenshot attacks destroy the bits DURING extraction.

---

## 💡 When QR Codes WOULD Help

✅ **Programmatic attacks with partial corruption**
- Match score > 0.90 but with minor bit errors
- 10-30% bit flips from compression
- Intentional damage to <30% of watermark

❌ **When QR Does NOT Help**
- Screenshot attacks (PSNR < 15 dB)
- Display-capture scenarios
- Severe compression/degradation

---

## 🎓 Conclusion

### For Screenshot Protection:
- **Don't use QR codes** - No benefit, 4x larger, more complex
- **Use visible watermarks** instead

### For Programmatic Attacks:
- **TEXT watermarks are sufficient**
- Consider QR only if you see partial corruption with TEXT

### Bottom Line:
**QR code watermarks are NOT worth it for this use case** ❌

---

## 📚 Full Details

See [QR_CODE_TEST_RESULTS.md](QR_CODE_TEST_RESULTS.md) for:
- Complete technical analysis
- Detailed failure breakdown
- Cost-benefit analysis
- Future test suggestions

---

**Test Date:** November 17, 2024  
**Conclusion:** Stick with TEXT watermarks ✓

