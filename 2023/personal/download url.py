import requests
from PIL import Image
from fpdf import FPDF
import io
import tempfile

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        raise Exception(f"Failed to download image from {url}")

def save_images_as_pdf(images, output_pdf):
    pdf = FPDF()
    for img in images:
        pdf.add_page()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img_file:
            img.convert("RGB").save(temp_img_file, format='PNG')
            temp_img_path = temp_img_file.name
        pdf.image(temp_img_path, x=0, y=0, w=pdf.w, h=pdf.h)
    pdf.output(output_pdf)

def main(base_url, total_pages):
    images = []
    for i in range(1, total_pages + 1):
        url = base_url.format(i)
        print(f"Downloading image from {url}")
        img = download_image(url)
        images.append(img)

    output_pdf = "combined_images.pdf"
    save_images_as_pdf(images, output_pdf)
    print(f"PDF saved as {output_pdf}")

if __name__ == "__main__":
    base_url = "https://image.slidesharecdn.com/mdi-valueinvestingincyclicals-220125070521/75/Value-Investing-In-Cylicals-A-Practioner-s-Insights-{}-2048.jpg"
    total_pages = int(input("Enter the total number of pages: "))
    main(base_url, total_pages)
