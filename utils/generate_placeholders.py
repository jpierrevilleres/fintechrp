from PIL import Image, ImageDraw, ImageFont
import os
from random import randint, choice

def create_gradient_background(width, height, color1, color2):
    """Create a gradient background"""
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return image

def add_overlay_pattern(image):
    """Add a semi-transparent pattern overlay"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for i in range(0, width, 20):
        for j in range(0, height, 20):
            if (i + j) % 40 == 0:
                draw.rectangle([i, j, i+10, j+10], fill=(255, 255, 255, 20))
    return image

def create_placeholder_image(filename, width, height, category, number=None):
    """Create a placeholder image with text and styling"""
    # Color schemes for different categories
    colors = {
        'finance': ((0, 87, 63), (0, 166, 120)),  # Green gradient
        'technology': ((25, 25, 112), (65, 105, 225)),  # Blue gradient
        'real-estate': ((139, 0, 0), (205, 92, 92)),  # Red gradient
    }
    
    # Create base image with gradient
    color1, color2 = colors.get(category, ((50, 50, 50), (100, 100, 100)))
    image = create_gradient_background(width, height, color1, color2)
    
    # Add pattern overlay
    add_overlay_pattern(image)
    
    # Add text
    draw = ImageDraw.Draw(image)
    
    # Draw category name
    text = f"{category.replace('-', ' ').title()}"
    if number:
        text += f" {number}"
    
    # Calculate text size and position
    font_size = min(width, height) // 10
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Add multiple design elements
    for i in range(5):
        x = randint(0, width)
        y = randint(0, height)
        size = randint(20, 100)
        opacity = randint(30, 100)
        draw.ellipse([x, y, x+size, y+size], 
                    fill=(255, 255, 255, opacity))
    
    # Draw text with shadow
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw shadow
    draw.text((x+2, y+2), text, fill=(0, 0, 0, 128), font=font)
    # Draw main text
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Save image
    image.save(filename, quality=95)

def main():
    # Ensure the static/img directory exists
    img_dir = os.path.join('static', 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    # Create banner image
    create_placeholder_image(
        os.path.join(img_dir, 'finance-banner.jpg'),
        1200, 400, 'finance'
    )
    
    # Create category thumbnails
    categories = ['finance', 'technology', 'real-estate']
    for category in categories:
        for i in range(1, 4):
            create_placeholder_image(
                os.path.join(img_dir, f'{category}-{i}.jpg'),
                800, 600, category, i
            )

if __name__ == '__main__':
    main()
    print("Sample images have been created successfully in the static/img directory!")