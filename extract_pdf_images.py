import fitz  # PyMuPDF
import os
import re
from pathlib import Path

pdf_path = "/Users/sahebjitsinghchhabra/Downloads/Products Ptoto.pdf"
output_dir = os.path.expanduser("~/Desktop/grand-website/images/products-safe/")
os.makedirs(output_dir, exist_ok=True)

# Known model names per page, extracted from text inspection
# We'll parse them dynamically from each page's text
# Pattern: things like "Ef-2 42S RWB", "GPA-50BL", "Marsvoice series-II ...", etc.

MODEL_PATTERN = re.compile(
    r'\b('
    r'Ef-2\s+[\w\-]+(?:\s+[\w\-/]+)*'       # Ef-2 variants
    r'|Ef-One\s+[\w\-]+(?:\s+[\w\-/]+)*'    # Ef-One variants
    r'|GPA[\-\s][\w\-/]+(?:\s+[\w]+)*'      # GPA variants
    r'|GES[\-\s]\d+\w*'                      # GES variants
    r'|GEH[\-\s]\d+\w*'                      # GEH variants
    r'|BBG\s+\d+\s+[\w\s]+'                  # BBG variants
    r'|Marsvoice\s+[\w\s\-]+'                # Marsvoice variants
    r'|Cometvoice[\w\s\-]*'                  # Cometvoice
    r'|Pursuitlite[\w\s\-]*'                 # Pursuitlite
    r'|GM\d+\w+'                             # GM codes
    r'|LED\s+[\w\s]+'                        # LED products
    r')',
    re.IGNORECASE
)

def slugify(name):
    """Convert a model name to a filename-safe slug."""
    name = name.strip()
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name)
    # Replace spaces and slashes with hyphens
    name = re.sub(r'[\s/]+', '-', name)
    # Remove characters that aren't alphanumeric, hyphen, or dot
    name = re.sub(r'[^\w\-]', '', name)
    # Collapse multiple hyphens
    name = re.sub(r'-+', '-', name)
    return name.lower().strip('-')

def extract_model_names(text):
    """Extract candidate model names from page text, preserving order."""
    seen = []
    seen_set = set()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip pure dimension lines
        if re.match(r'^Length\s*[-–]', line, re.IGNORECASE):
            continue
        if re.match(r'^\d+L', line):
            continue
        # Skip lines that are just numbers/measurements
        if re.match(r'^[\d\s,LmMWwxX\|\-]+$', line):
            continue
        # Try to match a model from this line
        match = MODEL_PATTERN.match(line)
        if match:
            candidate = match.group(1).strip()
        else:
            # Use the whole line as candidate if it looks like a model name
            # (not too long, not a sentence)
            if 2 < len(line) < 60 and not line.endswith('.') and len(line.split()) <= 7:
                candidate = line
            else:
                continue
        # Normalize candidate
        candidate = re.sub(r'\s+', ' ', candidate).strip()
        key = candidate.lower()
        if key not in seen_set:
            seen_set.add(key)
            seen.append(candidate)
    return seen

def get_image_extension(img_dict, xref, doc):
    """Determine the appropriate file extension for an image."""
    # Try colorspace and filter info from the image dict
    ext = img_dict.get('ext', '')
    if ext in ('jpeg', 'jpg'):
        return 'jpg'
    if ext in ('png',):
        return 'png'
    # Extract raw bytes to detect format
    try:
        base_image = doc.extract_image(xref)
        raw_ext = base_image.get('ext', 'jpg')
        if raw_ext in ('jpeg', 'jpg'):
            return 'jpg'
        if raw_ext == 'png':
            return 'png'
        return raw_ext
    except Exception:
        return 'jpg'

doc = fitz.open(pdf_path)

total_extracted = 0
skipped_small = 0
skipped_exists = 0
saved_new = []

# Track xrefs we've already saved to avoid duplicates within the PDF
saved_xrefs = set()

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    image_list = page.get_images(full=True)

    model_names = extract_model_names(text)

    print(f"\n=== Page {page_num+1} | {len(image_list)} images | Models found: {model_names}")

    # We'll assign model names to images by index (one name per significant image)
    # Filter out tiny images first to get the "real" product images
    significant_images = []
    for img in image_list:
        xref = img[0]
        try:
            base_image = doc.extract_image(xref)
        except Exception:
            continue
        w, h = base_image['width'], base_image['height']
        if w < 100 or h < 100:
            continue
        significant_images.append((xref, base_image, w, h))

    # Assign model names: cycle through models for each significant image
    # If there's only one model name and multiple images, use page-indexed suffix
    for img_index, (xref, base_image, w, h) in enumerate(significant_images):
        total_extracted += 1

        # Pick model name
        if model_names:
            if len(model_names) > img_index:
                model = model_names[img_index]
            else:
                # Repeat the last model name with index suffix
                model = f"{model_names[-1]}-variant-{img_index + 1}"
        else:
            model = f"page-{page_num + 1}-image-{img_index + 1}"

        ext = base_image.get('ext', 'jpg')
        if ext in ('jpeg',):
            ext = 'jpg'

        filename = slugify(model) + '.' + ext
        filepath = os.path.join(output_dir, filename)

        # Check if already exists
        if os.path.exists(filepath):
            print(f"  SKIP (exists): {filename}")
            skipped_exists += 1
            continue

        # Check if xref already saved under a different name
        if xref in saved_xrefs:
            print(f"  SKIP (xref duplicate): xref={xref}, would save as {filename}")
            skipped_exists += 1
            continue

        # Save
        with open(filepath, 'wb') as f:
            f.write(base_image['image'])
        saved_xrefs.add(xref)
        saved_new.append(filename)
        print(f"  SAVED ({w}x{h}): {filename}")

print("\n" + "="*60)
print(f"REPORT")
print(f"  Total significant images processed: {total_extracted}")
print(f"  Skipped (too small, <100x100):      {skipped_small}")
print(f"  Skipped (already exists):           {skipped_exists}")
print(f"  Saved new:                          {len(saved_new)}")
print(f"\nNew filenames saved:")
for fn in saved_new:
    print(f"  - {fn}")
