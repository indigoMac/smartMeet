from PIL import Image, ImageDraw, ImageFont
import os

# Create 16x16 icon
img16 = Image.new('RGB', (16, 16), color='#0078d4')
draw16 = ImageDraw.Draw(img16)
try:
    font16 = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 12)
except:
    font16 = ImageFont.load_default()
draw16.text((8, 8), 'S', fill='white', font=font16, anchor='mm')
img16.save('icon-16.png')

# Create 32x32 icon
img32 = Image.new('RGB', (32, 32), color='#0078d4')
draw32 = ImageDraw.Draw(img32)
try:
    font32 = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 20)
except:
    font32 = ImageFont.load_default()
draw32.text((16, 16), 'S', fill='white', font=font32, anchor='mm')
img32.save('icon-32.png')

# Create 80x80 icon
img80 = Image.new('RGB', (80, 80), color='#0078d4')
draw80 = ImageDraw.Draw(img80)
try:
    font80 = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 48)
except:
    font80 = ImageFont.load_default()
draw80.text((40, 40), 'S', fill='white', font=font80, anchor='mm')
img80.save('icon-80.png')

print('Icons created successfully') 