# Watermark Extraction Experiment - Documentation Index

This index helps you navigate all the experiment documentation and reports.

---

## 📚 Available Documents

### 1. 🆕 [QR_CODE_TEST_RESULTS.md](QR_CODE_TEST_RESULTS.md)
**QR Code vs Text Watermarking Comparison**

Answers the question: Does QR code error correction help with screenshot attacks?

- Test setup and methodology
- Screenshot attack results (QR vs TEXT)
- Visual evidence of QR code corruption
- Why QR error correction doesn't help
- When QR codes would/wouldn't help
- Cost-benefit analysis
- Final recommendations

**Best for:** Understanding QR code limitations, decision making

**Result:** ❌ QR codes provide NO advantage over text for screenshots

---

### 2. 📄 [WATERMARK_EXTRACTION_EXPERIMENT_REPORT.md](WATERMARK_EXTRACTION_EXPERIMENT_REPORT.md)
**The Complete Technical Report**

Comprehensive documentation including:
- Detailed experimental setup
- Complete methodology
- All test scenarios with results
- Technical analysis and metrics
- Conclusions and recommendations
- Future work suggestions

**Best for:** Technical review, academic reference, thorough understanding

---

### 3. ⚡ [EXPERIMENT_SUMMARY.md](EXPERIMENT_SUMMARY.md)
**Quick Reference Guide**

Executive summary with:
- Results at a glance (table format)
- What works / what fails
- Key findings and thresholds
- Quick recommendations
- Visual highlights

**Best for:** Quick overview, decision making, executive presentation

---

### 4. 🖼️ [VISUAL_COMPARISON.md](VISUAL_COMPARISON.md)
**Image Gallery & Visual Analysis**

Side-by-side comparisons featuring:
- All test images (original, attacked, recovered)
- Quality metrics visualizations
- Dimension flow diagrams
- Pixel-level comparisons
- Color and format analysis

**Best for:** Visual learners, presentations, quality assessment

---

## 🎯 Quick Navigation

### I want to...

**Understand what happened:**
→ Start with [EXPERIMENT_SUMMARY.md](EXPERIMENT_SUMMARY.md)

**See the images and results:**
→ Go to [VISUAL_COMPARISON.md](VISUAL_COMPARISON.md)

**Get full technical details:**
→ Read [WATERMARK_EXTRACTION_EXPERIMENT_REPORT.md](WATERMARK_EXTRACTION_EXPERIMENT_REPORT.md)

**Run the experiments myself:**
→ Use the scripts:
- `test_with_recovery.py` - Automated testing
- `extract_watermark.py` - Main extraction tool
- `create_good_screenshot_simulation.py` - Create test cases

---

## 📊 Key Findings Summary

### ✅ What Works
- **Programmatic crop+resize attacks** → Recovery-based extraction succeeds
- **Match scores >0.95** → Reliable watermark extraction
- **PSNR >30 dB** → Quality sufficient for recovery

### ❌ What Fails  
- **Real device screenshots** → Watermark destroyed (PSNR ~11 dB)
- **Match scores <0.85** → Unreliable parameter estimation
- **Display rendering** → Compound degradation effects
- **QR code watermarks** → No advantage over text for screenshots (tested ✓)

---

## 🔬 Test Results Overview

| Test | Match Score | PSNR | Result |
|------|-------------|------|--------|
| 80% Crop + 93% Resize | 0.9983 ⭐⭐⭐ | >30 dB | ✅ Success |
| 70% Crop + 70% Resize | 0.9957 ⭐⭐ | >30 dB | ⚠️ Partial |
| 95% Crop + 95% Resize | 0.9985 ⭐⭐⭐ | >30 dB | ✅ Success |
| Real Screenshot | 0.8018 ⚠️ | 11.24 dB | ❌ Failed |

**Pass Rate:** 60% overall, 100% for programmatic attacks, 0% for real screenshots

---

## 🛠️ Test Scripts & Tools

### Main Tools
- **`extract_watermark.py`** - Production extraction tool with auto-recovery
- **`embed_watermark.py`** - Watermark embedding tool

### Test Scripts
- **`test_with_recovery.py`** - Automated recovery workflow testing
- **`test_attack_resilience.py`** - Attack limitation testing
- **`create_good_screenshot_simulation.py`** - Proper simulation generation

### Test Data
- **`examples/pic/`** - Source images
- **`examples/output/`** - Generated test images and results

---

## 📈 Generated Test Images

### Successful Extractions ✅
```
examples/output/
├── attack_crop80_scale93.png ..................... Attacked (838×1815)
├── attack_crop80_scale93_recovered.png ........... Recovered ✅
├── attack_crop70_scale70.png ..................... Attacked (473×854)
├── attack_crop70_scale70_recovered.png ........... Recovered ⚠️
├── attack_crop95_scale95.png ..................... Attacked (962×2086)
└── attack_crop95_scale95_recovered.png ........... Recovered ✅
```

### Failed Extractions ❌
```
examples/output/
├── vd013_background_watermarked_simulated.png .... Real screenshot (1206×2622)
└── vd013_background_watermarked_simulated_recovered.png .. Failed recovery ❌
```

### Reference Images
```
examples/output/
├── vd013_background_watermarked.webp ............. Original watermarked (1126×2439)
└── vd013_background_watermarked_proper_simulation.png .. Programmatic simulation
```

---

## 🎓 Understanding the Results

### The Recovery Process
```
1. Parameter Estimation → Find crop region & scale
2. Image Recovery → Restore to original dimensions  
3. Watermark Extraction → Decode watermark bits
```

### Success Criteria
- ✅ Match Score >0.95 (parameter estimation accuracy)
- ✅ PSNR >30 dB (image quality preservation)
- ✅ Low pixel difference (<5 average)

### Why Screenshots Fail
```
Watermarked Image (WebP)
    ↓ Display Rendering (color space, gamma)
    ↓ Screenshot Tool (compression)
    ↓ Format Conversion (resampling)
    ↓ Resolution Effects (DPI, scaling)
Screenshot (PNG) → WATERMARK DESTROYED
    ↓ PSNR = 11.24 dB (severe degradation)
    ↓ Match Score = 0.8018 (poor)
    ↓ Extraction FAILS
```

---

## 💡 Recommendations

### Use This Technique For:
✅ Tracking programmatic image manipulation  
✅ Detecting unauthorized crop/resize  
✅ Digital workflow image tracking  

### Don't Use For:
❌ Screenshot protection (device-to-device)  
❌ Display-to-camera capture scenarios  
❌ Cross-platform image sharing  

### Best Practices:
1. **Always use recovery** when images may be cropped/resized
2. **Set SEARCH_NUM ≥ 500** for better accuracy
3. **Check match score** (>0.95 = reliable, <0.85 = unreliable)
4. **Verify PSNR** of recovered images (>30 dB required)

---

## 📞 Quick Reference

### Configuration Values Used
```python
WATERMARK_LENGTH = 334  # bits
PASSWORD_IMG = 1
PASSWORD_WM = 1
SEARCH_NUM = 500  # search iterations
SCALE_RANGE = (0.5, 2)  # scale factor range
```

### Critical Thresholds
- **Match Score:** >0.95 excellent, 0.85-0.95 good, <0.85 unreliable
- **PSNR:** >30 dB required, <15 dB = watermark destroyed
- **Pixel Difference:** <5 good, >30 = severe degradation

---

## 🔗 Related Documentation

### Project Documentation
- `README.md` - Project overview
- `WATERMARK_USAGE.md` - Usage instructions
- `QUICK_REFERENCE.md` - Command quick reference
- `CHANGES_SUMMARY.md` - Project changes

### Library Documentation
- [blind_watermark GitHub](https://github.com/guofei9987/blind_watermark)
- Library docs: `docs/`

---

## 📅 Document History

| Date | Document | Version |
|------|----------|---------|
| 2024-11-17 | Experiment Report | 1.0 |
| 2024-11-17 | Summary | 1.0 |
| 2024-11-17 | Visual Comparison | 1.0 |
| 2024-11-17 | Index | 1.0 |

---

## 🎯 Next Steps

### For Reviewers:
1. Read [EXPERIMENT_SUMMARY.md](EXPERIMENT_SUMMARY.md) for overview
2. Check [VISUAL_COMPARISON.md](VISUAL_COMPARISON.md) for image evidence
3. Review [full report](WATERMARK_EXTRACTION_EXPERIMENT_REPORT.md) for details

### For Users:
1. Understand limitations (screenshots won't work)
2. Use `extract_watermark.py` for extraction
3. Always enable recovery for attacked images
4. Check match scores before trusting results

### For Developers:
1. Review test scripts for methodology
2. Run `test_with_recovery.py` to reproduce results
3. Examine `extract_watermark.py` for implementation
4. Consider improvements listed in full report

---

**Happy Reading! 📖**

For questions or issues, refer to the appropriate document above or check the test scripts for implementation details.

