from PIL import Image, ImageDraw, ImageFont
import os

# Create 64x64 icon
img64 = Image.new('RGB', (64, 64), color='#0078d4')
draw64 = ImageDraw.Draw(img64)
try:
    font64 = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 40)
except:
    font64 = ImageFont.load_default()
draw64.text((32, 32), 'S', fill='white', font=font64, anchor='mm')
img64.save('icon-64.png')

# Create 128x128 icon
img128 = Image.new('RGB', (128, 128), color='#0078d4')
draw128 = ImageDraw.Draw(img128)
try:
    font128 = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 80)
except:
    font128 = ImageFont.load_default()
draw128.text((64, 64), 'S', fill='white', font=font128, anchor='mm')
img128.save('icon-128.png')

print('Missing icons (64x64 and 128x128) created successfully') 