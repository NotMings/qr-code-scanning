from PIL import Image, ImageGrab
from pyzbar import pyzbar


def resize(w_box, h_box, pil_image):
    w, h = pil_image.size
    f1 = 1.0 * w_box / w
    f2 = 1.0 * h_box / h
    factor = min([f1, f2])
    width = int(w * factor)
    height = int(h * factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)


def screen_shot():
    return ImageGrab.grab()


def processing_image(image, position):
    x1, y1, x2, y2 = position
    cropped = image.crop((x1, y1, x2, y2))
    cropped.show()
    return cropped.convert('L')


def decode_qr_code(image):
    image_obj = pyzbar.decode(image)
    if image_obj:
        for barcode in image_obj:
            content = barcode.data.decode('UTF-8')
        return content
    return False
