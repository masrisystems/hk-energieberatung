"""
Batch conversion and verification script for HK Energieberatung GBP product images.
Takes source images (from brain generation and assets), applies 1:1 square framing where needed,
and converts each image to an SEO-named WebP file in assets/img/gbp/ using convert-to-webp.py.
"""

import os
import sys
from pathlib import Path
from PIL import Image

def make_square_crop(image: Image.Image) -> Image.Image:
    width, height = image.size
    if width == height:
        return image
    
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    return image.crop((left, top, right, bottom))

def process_all_gbp_images():
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "assets" / "img" / "gbp"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    brain_dir = Path(r"C:\Users\super\.gemini\antigravity-ide\brain\2331a693-38e3-4511-8ae6-e38d8524394e")
    assets_img_dir = base_dir / "assets" / "img"
    temp_dir = brain_dir / "scratch" / "temp_crops"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    mapping = [
        (1, "sanierungsfahrplan-isfp-foerderung", brain_dir / "gbp_isfp_plan_1787083900034.jpg"),
        (2, "energieverbrauchsausweis-wohngebaeude", brain_dir / "gbp_verbrauchsausweis_1787083912844.jpg"),
        (3, "energieberater-bremen", brain_dir / "gbp_berater_bremen_1787083923980.jpg"),
        (4, "kfw-458-heizungsfoerderung-70-prozent", brain_dir / "gbp_kfw_waermepumpe_1787083936222.jpg"),
        (5, "bafa-foerderung-daemmung-2026", brain_dir / "gbp_bafa_daemmung_1787083949486.jpg"),
        (6, "kfw-261-effizienzhaus-sanierung", brain_dir / "gbp_kfw_effizienzhaus_1787083963163.jpg"),
        (7, "energetische-baubegleitung-foerderung-niedersachsen", brain_dir / "gbp_baubegleitung_1787083976346.jpg"),
        (8, "hydraulischer-abgleich-verfahren-b", brain_dir / "gbp_hydraulischer_abgleich_1787083990338.jpg"),
        (9, "foerdermittel-fenstertausch-energieberater", brain_dir / "gbp_fenstertausch_1787084002757.jpg"),
        (10, "energieberater-aurich", brain_dir / "gbp_berater_aurich_1787084016331.jpg"),
        (11, "energiebedarfsausweis-wohngebaeude-berechnen", brain_dir / "gbp_bedarfsausweis_1787084037710.jpg"),
        (12, "thermografie-energieberatung-waermebild", brain_dir / "gbp_thermografie_1787084052761.jpg"),
        (13, "kellerdeckendaemmung-dachboden-foerderung", brain_dir / "gbp_dachbodendaemmung_1787084069079.jpg"),
        (14, "foerdermittelberatung-energieberater-zuschuss", assets_img_dir / "bafa.jpg"),
        (15, "vor-ort-energieberatung-norddeutschland", assets_img_dir / "services.jpg"),
        (16, "energieberatung-mehrfamilienhaus-weg", assets_img_dir / "apartment-beverage-bottle-544112-1536x1152.jpg"),
        (17, "technische-projektbeschreibung-tpb-bafa", assets_img_dir / "about-main.png"),
        (18, "blower-door-test-luftdichtheitsmessung", assets_img_dir / "about-banner.jpg"),
        (19, "photovoltaik-solarthermie-beratung-energieberater", assets_img_dir / "hero.jpg"),
        (20, "heizungsoptimierung-foerderung-beg-em", assets_img_dir / "kfw.jpg")
    ]
    
    convert_script = base_dir / "scripts" / "convert-to-webp.py"
    from importlib.machinery import SourceFileLoader
    converter = SourceFileLoader("converter", str(convert_script)).load_module()
    
    results = []
    
    print("=== Processing & Converting All 20 GBP Images ===")
    for priority, kw, src_path in mapping:
        if not src_path.exists():
            print(f"FAILED: Source missing for Product {priority}: {src_path}")
            results.append((priority, kw, False, "Source missing", ""))
            continue
        
        # Load and square-crop if necessary
        with Image.open(src_path) as img:
            sq_img = make_square_crop(img)
            temp_crop_path = temp_dir / f"crop_{priority}_{src_path.stem}.png"
            sq_img.save(temp_crop_path, "PNG")
        
        # Convert to WebP using designated convert-to-webp script
        final_filename = f"hk-energieberatung-{kw}.webp"
        final_path = output_dir / final_filename
        
        success = converter.convert_to_webp(str(temp_crop_path), str(final_path), quality=88, max_dimension=1080)
        
        if success and final_path.exists():
            with Image.open(final_path) as verified:
                size_kb = final_path.stat().st_size / 1024
                dim_str = f"{verified.size[0]}x{verified.size[1]}"
                format_str = verified.format
                print(f"[OK] Priority {priority:02d}: {final_filename} | {dim_str} | {format_str} | {size_kb:.1f} KB")
                results.append((priority, kw, True, final_filename, f"{dim_str}, {size_kb:.1f} KB"))
        else:
            print(f"[FAIL] Priority {priority:02d}: Conversion failed for {final_filename}")
            results.append((priority, kw, False, final_filename, "Conversion failed"))
            
    print("\n=== Verification Summary ===")
    all_ok = all(r[2] for r in results)
    print(f"Total processed: {len(results)}/20 | All Valid: {all_ok}")
    return results

if __name__ == "__main__":
    process_all_gbp_images()
