"""
card_layout.py
--------------
Tunable coordinate constants for ID card composition.
Templates: newID_Front.png (front) and newID_Back.png (back)
Both are 638 x 1011 px RGBA.

FRONT layout (visual inspection):
  - SPACE. logo:           y=80-200  (baked in)
  - Open dark area:        y=220-940 (we own this zone)
  - "Instructor" banner:   y=950-1011 (baked in)

BACK layout (visual inspection):
  - SPACE. logo + tagline: y=80-240  (baked in)
  - Open dark area:        y=260-550 (we own this zone for text)
  - Two baked-in QR codes: y=560-790 (baked in — do NOT write here)
  - Website footer:        y=900-1000 (baked in)

Edit these values to fine-tune placement without touching generation logic.
"""
import os

# ─────────────────────────────────────────────────────────
# Template file paths
# _HERE = backend/app/services -> 3 levels up = PortalV2
# ─────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))

FRONT_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "newID_Front.png")
BACK_TEMPLATE_PATH  = os.path.join(TEMPLATE_DIR, "newID_Back.png")

# ──────────────────────────────────────────────────────────
# FRONT CARD  (newID_Front.png — 638 x 1011)
# ──────────────────────────────────────────────────────────

# Profile photo — large circle, horizontally centered, upper portion of open area
FRONT_PHOTO_SIZE = 220          # circle diameter in pixels
FRONT_PHOTO_CX   = 319          # horizontal center (W / 2)
FRONT_PHOTO_CY   = 370          # vertical center of the circle

# Instructor name — big, centered below the photo
FRONT_NAME_CX        = 319      # horizontal center for centering text
FRONT_NAME_Y         = 505      # Y of the top of the name text block
FRONT_NAME_COLOR     = (255, 255, 255)   # white
FRONT_NAME_FONT_SIZE = 34

# LinkedIn QR code — lower section, above the "Instructor" banner at y=950
FRONT_QR_SIZE = 190             # QR square side in pixels (keep crisp)
FRONT_QR_X    = 319 - 95        # left edge = CX - QR_SIZE/2  (horizontally centered)
FRONT_QR_Y    = 705             # top of QR box

# ──────────────────────────────────────────────────────────
# BACK CARD  (newID_Back.png — 638 x 1011)
# ──────────────────────────────────────────────────────────

# ID Number text block (inside dark open area y=260-550)
BACK_ID_LABEL_X      = 60
BACK_ID_LABEL_Y      = 295
BACK_ID_VALUE_X      = 60
BACK_ID_VALUE_Y      = 320

# Issue Date text block
BACK_DATE_LABEL_X    = 60
BACK_DATE_LABEL_Y    = 400
BACK_DATE_VALUE_X    = 60
BACK_DATE_VALUE_Y    = 425

# Text colors
BACK_LABEL_COLOR     = (160, 130, 200)   # muted light purple for labels
BACK_VALUE_COLOR     = (255, 255, 255)   # white for values

# Font sizes
BACK_LABEL_FONT_SIZE = 13
BACK_VALUE_FONT_SIZE = 26
