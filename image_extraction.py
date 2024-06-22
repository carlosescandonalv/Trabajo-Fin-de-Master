from icrawler.builtin import GoogleImageCrawler
import shutil
import os
from PIL import Image

def clear_directory(directory):
    if os.path.exists(directory) and os.listdir(directory):
        # Delete all contents of the directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print(f"All contents of the directory '{directory}' have been deleted.")
    else:
        print(f"The directory '{directory}' is empty or does not exist.")

def image_extraction(string):
  clear_directory("images")
  google_Crawler = GoogleImageCrawler()
  google_Crawler.crawl(keyword = string, max_num = 3)

def find_first_valid_image(directory):
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"The directory '{directory}' does not exist.")
        return None
    
    # Iterate through files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify that it is, in fact, an image
            print(f"Found a valid image: {file_path}")
            return file_path
        except (IOError, SyntaxError) as e:
            # Print error message if the file is not a valid image
            print(f"Invalid image file: {file_path}. Reason: {e}")

    print("No valid images found in the directory.")
    return None


image_extraction("Kylian Mbappé")