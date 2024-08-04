from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re

# Path to your CAPTCHA image
image_path = "JPP4222973115888816773.gif"  # Update this to the correct path

# Load the image
try:
    image = Image.open(image_path)
except FileNotFoundError:
    raise FileNotFoundError(f"Unable to load image from the path: {image_path}")

# Preprocess the image for better OCR
def preprocess_image(image):
    # Convert image to grayscale
    gray_image = image.convert('L')
    
    # Enhance the contrast
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2.0)
    
    # Apply a filter to remove noise
    filtered_image = enhanced_image.filter(ImageFilter.MedianFilter(size=3))
    
    return filtered_image

# Preprocess the image
preprocessed_image = preprocess_image(image)

# Save the preprocessed image (optional, for debugging)
preprocessed_image_path = "preprocessed_image.png"
preprocessed_image.save(preprocessed_image_path)

# Use Tesseract to do OCR on the preprocessed image
captcha_text = pytesseract.image_to_string(preprocessed_image, config='--psm 8')

print("Extracted CAPTCHA Text:", captcha_text)

# Clean the extracted text to get only numbers
captcha_number = re.findall(r'\d+', captcha_text)
captcha_number = ''.join(captcha_number)

print("Extracted CAPTCHA Number:", captcha_number)
