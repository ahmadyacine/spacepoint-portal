"""
id_card_service.py
------------------
Generates instructor ID card images (front + back) by compositing
dynamic content onto newID_Front.png / newID_Back.png using Pillow.

Front card overlays:
  - Large circular profile photo
  - Instructor full name (big, centered)
  - LinkedIn QR code (bottom section)

Back card overlays:
  - ID Number label + value
  - Issue Date label + value
  (All other content is already baked into the back template)
"""
import io
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.image.pil import PilImage

from app.services.card_layout import (
    FRONT_TEMPLATE_PATH, BACK_TEMPLATE_PATH,
    # Front
    FRONT_PHOTO_SIZE, FRONT_PHOTO_CX, FRONT_PHOTO_CY,
    FRONT_NAME_CX, FRONT_NAME_Y, FRONT_NAME_COLOR, FRONT_NAME_FONT_SIZE,
    FRONT_QR_SIZE, FRONT_QR_X, FRONT_QR_Y,
    # Back
    BACK_ID_LABEL_X, BACK_ID_LABEL_Y, BACK_ID_VALUE_X, BACK_ID_VALUE_Y,
    BACK_DATE_LABEL_X, BACK_DATE_LABEL_Y, BACK_DATE_VALUE_X, BACK_DATE_VALUE_Y,
    BACK_LABEL_COLOR, BACK_VALUE_COLOR, BACK_LABEL_FONT_SIZE, BACK_VALUE_FONT_SIZE,
)

# ── Uploads base dir ───────────────────────────────────────────────────────
_THIS_DIR    = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.normpath(os.path.join(_THIS_DIR, "..", ".."))
UPLOADS_BASE = os.path.join(_BACKEND_DIR, "app", "uploads", "instructor_cards")


# ── Font loader ─────────────────────────────────────────────────────────────

def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Try Windows system fonts; fall back to Pillow default."""
    candidates = []
    if bold:
        candidates = [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
            r"C:\Windows\Fonts\verdanab.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
            r"C:\Windows\Fonts\verdana.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ── QR generator ───────────────────────────────────────────────────────────

def generate_qr(url: str, size: int) -> Image.Image:
    """Generate a crisp black/white QR code at exactly `size` px square."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white", image_factory=PilImage)
    img = img.convert("RGBA").resize((size, size), Image.LANCZOS)
    return img


# ── Circle crop ────────────────────────────────────────────────────────────

def circle_crop(photo: Image.Image, diameter: int) -> Image.Image:
    """Resize photo to square and crop to anti-aliased circle."""
    photo = photo.convert("RGBA").resize((diameter, diameter), Image.LANCZOS)
    mask  = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter, diameter), fill=255)
    result = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    result.paste(photo, (0, 0))
    result.putalpha(mask)
    return result


# ── Front card ─────────────────────────────────────────────────────────────

def generate_front_card(
    profile_photo_path: str,
    linkedin_url: str,
    name: str,
) -> Image.Image:
    """Compose the front ID card on newID_Front.png."""
    card = Image.open(FRONT_TEMPLATE_PATH).convert("RGBA")
    overlay = Image.new("RGBA", card.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 1. Profile photo — large circle centered at (FRONT_PHOTO_CX, FRONT_PHOTO_CY)
    try:
        photo = Image.open(profile_photo_path)
        circle = circle_crop(photo, FRONT_PHOTO_SIZE)
        paste_x = FRONT_PHOTO_CX - FRONT_PHOTO_SIZE // 2
        paste_y = FRONT_PHOTO_CY - FRONT_PHOTO_SIZE // 2
        overlay.paste(circle, (paste_x, paste_y), circle)
    except Exception as e:
        print(f"[id_card_service] Profile photo error: {e}")

    # 2. Instructor name — big, centered below the photo
    try:
        font = _load_font(FRONT_NAME_FONT_SIZE, bold=True)
        # Measure text width for centering
        bbox   = draw.textbbox((0, 0), name, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(
            (FRONT_NAME_CX - text_w // 2, FRONT_NAME_Y),
            name,
            fill=(*FRONT_NAME_COLOR, 255),
            font=font,
        )
    except Exception as e:
        print(f"[id_card_service] Name text error: {e}")

    # 3. LinkedIn QR code — bottom section above the Instructor banner
    try:
        qr_img = generate_qr(linkedin_url, FRONT_QR_SIZE)
        # Add subtle rounded white background behind QR for contrast
        qr_bg = Image.new("RGBA", (FRONT_QR_SIZE + 12, FRONT_QR_SIZE + 12), (255, 255, 255, 250))
        overlay.paste(qr_bg, (FRONT_QR_X - 6, FRONT_QR_Y - 6), qr_bg)
        overlay.paste(qr_img, (FRONT_QR_X, FRONT_QR_Y), qr_img)
    except Exception as e:
        print(f"[id_card_service] QR generation error: {e}")

    # Composite overlay onto card
    card = Image.alpha_composite(card, overlay)
    return card.convert("RGB")


# ── Back card ──────────────────────────────────────────────────────────────

def generate_back_card(
    instructor_id: str,
    issue_date: datetime,
) -> Image.Image:
    """Compose the back ID card on newID_Back.png."""
    card = Image.open(BACK_TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(card)

    label_font = _load_font(BACK_LABEL_FONT_SIZE, bold=False)
    value_font = _load_font(BACK_VALUE_FONT_SIZE, bold=True)

    date_str = issue_date.strftime("%d %B %Y") if issue_date else "—"

    # ID Number
    draw.text(
        (BACK_ID_LABEL_X, BACK_ID_LABEL_Y),
        "ID NUMBER",
        fill=(*BACK_LABEL_COLOR, 255),
        font=label_font,
    )
    draw.text(
        (BACK_ID_VALUE_X, BACK_ID_VALUE_Y),
        instructor_id,
        fill=(*BACK_VALUE_COLOR, 255),
        font=value_font,
    )

    # Issue Date
    draw.text(
        (BACK_DATE_LABEL_X, BACK_DATE_LABEL_Y),
        "ISSUE DATE",
        fill=(*BACK_LABEL_COLOR, 255),
        font=label_font,
    )
    draw.text(
        (BACK_DATE_VALUE_X, BACK_DATE_VALUE_Y),
        date_str,
        fill=(*BACK_VALUE_COLOR, 255),
        font=value_font,
    )

    return card.convert("RGB")


# ── Save to disk ───────────────────────────────────────────────────────────

def save_instructor_cards(
    user_id: int,
    front_img: Image.Image,
    back_img: Image.Image,
) -> tuple[str, str]:
    """Save front and back card images. Returns (front_path, back_path)."""
    out_dir = os.path.join(UPLOADS_BASE, str(user_id))
    os.makedirs(out_dir, exist_ok=True)

    front_path = os.path.join(out_dir, "front.png")
    back_path  = os.path.join(out_dir, "back.png")

    front_img.save(front_path, "PNG")
    back_img.save(back_path,  "PNG")

    return front_path, back_path


# ── ID assignment ──────────────────────────────────────────────────────────

def assign_instructor_id(db_count: int) -> str:
    """Generate a sequential instructor ID: SP-INS-0001, SP-INS-0002, …"""
    return f"SP-INS-{db_count + 1:04d}"
