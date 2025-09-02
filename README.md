# Image Steganography Tool

**IKB21303 Assignment 2 - Data Hiding & Encryption**  
*UniKL MIIT | July 2025*

## About

This is my Image Steganography Tool developed for Assignment 2 in IKB21303 (Data Hiding & Encryption). The application uses LSB (Least Significant Bit) technique to hide files inside images and provides analysis tools to compare results.

## Features

✅ **Hide Files**: Text files, PDFs, documents, and images  
✅ **Extract Files**: Retrieve hidden data from stego images  
✅ **Image Analysis**: Compare original vs stego with histograms  
✅ **Quality Metrics**: PSNR, MSE calculations  
✅ **File Size Analysis**: Detailed comparison with explanations  

## How to Run

1. Install requirements:
pip install opencv-python pillow numpy matplotlib

3. Run the application:
python steganography_gui.py


## Usage

1. **Hide Data Tab**: Select cover image → Choose secret file → Generate stego image
2. **Extract Data Tab**: Load stego image → Extract hidden file  
3. **Analysis Tab**: Compare images → View histograms and metrics

## Files Included

- `steganography_gui.py` - Main GUI application
- `steganography_tool.py` - Core LSB algorithms
- Sample images and files for testing

## Assignment Requirements Met

- ✅ Hide multiple file types (text, PDF, documents, images)
- ✅ Generate stego images  
- ✅ Visual quality analysis with histograms
- ✅ File size comparison and explanation
- ✅ Professional GUI interface

## Results Example

| Metric | Original | Stego | Change |
|--------|----------|-------|---------|
| Size (bytes) | 425,894 | 425,915 | +0.0049% |
| PSNR (dB) | - | 45.32 | Excellent Quality |

**Why similar file sizes?** LSB technique only modifies the least significant bit of pixels, causing minimal size changes while maintaining image quality.

## Student Information

**Course**: IKB21303 - Data Hiding & Encryption  
**Lecturer**: Dr. Delina Beh Mei Yin  
**Institution**: UniKL MIIT  
**Semester**: July 2025

---

*This tool demonstrates practical implementation of steganographic techniques with comprehensive analysis capabilities as required by the assignment rubric.*
