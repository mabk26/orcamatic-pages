"""Build a clean, typographic Open Graph card for orcamatic.com.

Fonts come from the repo's own self-hosted variable woff2 files (SIL OFL),
instantiated to static weights with fontTools. Nothing here is invented:
the copy matches the homepage, and no fake product screenshot is used.
"""
import pathlib
import tempfile
from fontTools import ttLib
from fontTools.varLib import instancer
from PIL import Image, ImageDraw, ImageFont

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path(tempfile.mkdtemp(prefix='ogbuild-'))  # static font instances, not published
FONTS = REPO / 'assets' / 'fonts'

def instantiate(src, dst, wght):
    f = ttLib.TTFont(FONTS / src)
    f = instancer.instantiateVariableFont(f, {'wght': wght}, inplace=False)
    f.save(OUT / dst)
    return OUT / dst

inter = instantiate('inter-latin-wght.woff2', 'inter.ttf', 400)
inter_med = instantiate('inter-latin-wght.woff2', 'inter-500.ttf', 500)
inter_bold = instantiate('inter-latin-wght.woff2', 'inter-700.ttf', 700)
serif = instantiate('newsreader-latin-wght.woff2', 'news.ttf', 500)
serif_semi = instantiate('newsreader-latin-wght.woff2', 'news-600.ttf', 600)
serif_italic = instantiate('newsreader-latin-wght-italic.woff2', 'news-it.ttf', 600)

W, H = 1200, 630
PAPER = (251, 251, 247)
INK = (16, 22, 42)
MUTED = (93, 102, 125)
VIOLET = (98, 85, 231)
VIOLET_DEEP = (64, 52, 183)
LINE = (216, 221, 236)
MINT = (201, 243, 230)

img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img, 'RGBA')

# soft violet wash, top-right
wash = Image.new('RGBA', (W, H), (0, 0, 0, 0))
dw = ImageDraw.Draw(wash)
dw.ellipse([W - 620, -380, W + 420, 460], fill=(238, 236, 255, 255))
dw.ellipse([W - 330, -170, W + 210, 250], fill=(201, 243, 230, 120))
img = Image.alpha_composite(img.convert('RGBA'), wash).convert('RGB')
d = ImageDraw.Draw(img, 'RGBA')

M = 84
def font(path, size):
    return ImageFont.truetype(str(path), size)

f_brand = font(serif_semi, 40)
f_tag = font(inter_med, 16)
f_h1 = font(serif_semi, 100)
f_h1i = font(serif_italic, 100)
f_body = font(inter, 23)
f_pill = font(inter_bold, 20)
f_small = font(inter_med, 19)

# brand row
icon = Image.open(REPO / 'assets' / 'orca-icon.png').convert('RGBA').resize((52, 52), Image.LANCZOS)
img.paste(icon, (M, 58), icon)
d.text((M + 68, 58), 'Orcamatic', font=f_brand, fill=INK)
d.text((M + 68, 110), 'BROWSER AUTOMATION', font=f_tag, fill=MUTED)

# headline
y = 196
d.text((M, y), 'Show it once.', font=f_h1, fill=INK)
d.text((M, y + 104), 'Let it ', font=f_h1, fill=INK)
hw = d.textlength('Let it ', font=f_h1)
d.text((M + hw, y + 104), 'run.', font=f_h1i, fill=VIOLET)

# body copy
def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if d.textlength(trial, font=f) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines

body = 'ORCA turns the clicking, typing and copying you repeat into saved workflows that run in your browser.'
by = 400
for line in wrap(body, f_body, 560):
    d.text((M, by), line, font=f_body, fill=MUTED)
    by += 34

# CTA pill
py = 500
label = 'Add ORCA to Chrome'
tw = d.textlength(label, font=f_pill)
pill_w = 30 + tw + 16 + 22 + 28
d.rounded_rectangle([M, py, M + pill_w, py + 54], radius=27, fill=VIOLET)
d.text((M + 30, py + 15), label, font=f_pill, fill=(255, 255, 255))
ax, ay = M + 30 + tw + 16, py + 20   # hand-drawn diagonal arrow (Inter has no U+2197)
d.line([ax + 2, ay + 18, ax + 18, ay + 2], fill=(255, 255, 255), width=3)
d.line([ax + 6, ay + 2, ax + 18, ay + 2], fill=(255, 255, 255), width=3)
d.line([ax + 18, ay + 2, ax + 18, ay + 14], fill=(255, 255, 255), width=3)

# right-side rule card, echoing the extension's step list
card = [700, 120, 1136, 500]
d.rounded_rectangle(card, radius=24, fill=(255, 255, 255), outline=LINE, width=2)
d.text((card[0] + 32, card[1] + 30), 'Weekly claim intake', font=font(serif_semi, 29), fill=INK)
d.text((card[0] + 32, card[1] + 68), 'Saved workflow \u00b7 5 steps', font=font(inter_med, 17), fill=MUTED)
steps = ['Click "New claim"  \u00b7  retry x3', 'Fill claimant email  \u00b7  from sheet', 'Select priority  \u00b7  wait 1.5s', 'Extract reference  \u00b7  to sheet', 'Submit form  \u00b7  on success']
sy = card[1] + 104
for i, s in enumerate(steps, 1):
    d.rounded_rectangle([card[0] + 32, sy, card[2] - 32, sy + 42], radius=11, fill=(248, 249, 254), outline=(227, 231, 240), width=1)
    d.rounded_rectangle([card[0] + 44, sy + 13, card[0] + 62, sy + 31], radius=9, fill=MINT)
    d.text((card[0] + 49, sy + 14), str(i), font=font(inter_bold, 15), fill=(9, 122, 106))
    d.text((card[0] + 76, sy + 12), s, font=font(inter, 17), fill=(56, 67, 94))
    sy += 48

# domain, bottom right
domain = 'orcamatic.com'
d.text((W - M - d.textlength(domain, font=f_small), 528), domain, font=f_small, fill=MUTED)

img.save(REPO / 'assets' / 'og-image.jpg', quality=90, optimize=True, progressive=True)
img.save(OUT / 'preview.png')  # eyeball this before committing the card
print('wrote og-image.jpg')
