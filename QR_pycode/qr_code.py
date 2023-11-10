import qrcode
import sys
import qrcode.image.svg


# if no arguments are passed, print help text and exit
if len(sys.argv) == 1:
    print("Usage: python qr_code.py <url>")
    sys.exit(1)

# read the url from command line
data = sys.argv[1]


# Generate QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(data)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image(fill_color="black", back_color="white")

# Save the QR code to a file
img.save("qrcode.png")


# Simple factory, just a set of rects.
factory = qrcode.image.svg.SvgImage
img = qrcode.make(data, image_factory=factory)

img.save("qrcode.svg")

