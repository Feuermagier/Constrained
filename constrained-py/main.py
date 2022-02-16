from PIL import ImageFont

for i in range(100):
    font = ImageFont.truetype("times.ttf", 12)
    font.getsize("Hello World!")