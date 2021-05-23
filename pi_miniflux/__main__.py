from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
from dotenv import load_dotenv
import os
from datetime import datetime
from io import BytesIO
import base64
import miniflux

load_dotenv()

USER_NAME = os.getenv('USERNAME')
API_KEY = os.getenv('API_KEY')
CATEGORY_ID = os.getenv('CATEGORY_ID')
MINIFLUX_HOST = os.getenv('MINIFLUX_HOST')

ICON_GUTTER_WIDTH = 40
SPACING = 4

client = client = miniflux.Client(MINIFLUX_HOST, api_key=API_KEY)

inky_display = InkyPHAT("black")
inky_display.set_border(inky_display.WHITE)
font = ImageFont.truetype(
    "/usr/share/fonts/truetype/darkergrotesque/DarkerGrotesque-ExtraBold.ttf", 18)


def wrap_text(text, width, font):
    text_lines = []
    text_line = []
    text = text.replace('\n', ' [br] ')
    words = text.split()

    for word in words:
        if word == '[br]':
            text_lines.append(' '.join(text_line))
            text_line = []
            continue
        text_line.append(word)
        w, _ = font.getsize(' '.join(text_line))
        if w > width:
            text_line.pop()
            text_lines.append(' '.join(text_line))
            text_line = [word]

    if len(text_line) > 0:
        text_lines.append(' '.join(text_line))

    return text_lines

def draw_text(draw, headline):
    GUTTER_WIDTH = ICON_GUTTER_WIDTH + (SPACING * 2)
    lines = wrap_text(headline, inky_display.WIDTH - GUTTER_WIDTH, font)
    y_text = 0

    for line in lines:
        _, height = font.getsize(line)
        draw.text((GUTTER_WIDTH, y_text), line, inky_display.BLACK, font)
        y_text += height


def draw_favicon(img, encoded_favicon):
    print(encoded_favicon)
    favicon = Image.open(BytesIO(base64.b64decode(encoded_favicon)))
    large_fav = favicon.resize((ICON_GUTTER_WIDTH, ICON_GUTTER_WIDTH), Image.LANCZOS)
    CENTERED_IMG = (inky_display.HEIGHT / 2) - (ICON_GUTTER_WIDTH / 2)
    img.paste(large_fav, (int(SPACING / 2), int(CENTERED_IMG)), large_fav)


def draw_headline(headline, encoded_favicon):
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)
    draw_text(draw, headline)
    draw_favicon(img, encoded_favicon)
    inky_display.set_image(img)
    inky_display.show()


def main():
    feeds = client.get_entries(category_id=CATEGORY_ID, status=['read', 'unread'], limit=1, order='published_at', direction='desc')
    recent_story = feeds.get('entries')[0]
    icon_data = recent_story.get('feed').get('icon')
    icon = client.get_feed_icon(feed_id=icon_data.get('feed_id'))
    draw_headline(recent_story.get('title'), icon.get('data').split(',')[1])
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print("Updated story!", current_time)

if __name__ == '__main__':
    main()
