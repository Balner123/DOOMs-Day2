from PIL import Image
import numpy as np
import cv2

# Načtení původního obrázku s alfa kanálem
original_image = Image.open("1.png").convert("RGBA")
w, h = original_image.size
target_size = (512, 512)  # Cílová velikost

# Nastavení parametrů
rotation_angle = -18  # úhel otočení
num_frames = 20       # počet snímků
tilt_factor = 0.6     # míra zploštění (0.0 až 1.0)

for i in range(num_frames):
    # Výpočet aktuálního úhlu otočení
    angle = i * rotation_angle

    # Rotace obrázku
    rotated_image = original_image.rotate(angle, resample=Image.BICUBIC, expand=True)
    rotated_w, rotated_h = rotated_image.size

    # Konverze na NumPy pole s alfa kanálem pro OpenCV
    rotated_np = np.array(rotated_image)

    # Rozdělení na RGB a alfa kanál
    bgr = cv2.cvtColor(rotated_np[:, :, :3], cv2.COLOR_RGBA2BGRA)
    alpha = rotated_np[:, :, 3]

    # Nastavení transformační matice pro naklonění směrem dozadu (3D efekt)
    src_points = np.float32([
        [0, 0],
        [rotated_w, 0],
        [0, rotated_h],
        [rotated_w, rotated_h]
    ])
    dst_points = np.float32([
        [0, rotated_h * (1 - tilt_factor) / 2],
        [rotated_w, rotated_h * (1 - tilt_factor) / 2],
        [0, rotated_h * (1 + tilt_factor) / 2],
        [rotated_w, rotated_h * (1 + tilt_factor) / 2]
    ])
    perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Aplikace 3D naklonění na RGB i alfa kanál
    bgr_tilted = cv2.warpPerspective(bgr, perspective_matrix, (rotated_w, rotated_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    alpha_tilted = cv2.warpPerspective(alpha, perspective_matrix, (rotated_w, rotated_h), borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    # Sloučení RGB a alfa kanálu zpět
    tilted_np = cv2.merge((bgr_tilted[:, :, 0], bgr_tilted[:, :, 1], bgr_tilted[:, :, 2], alpha_tilted))
    tilted_image = Image.fromarray(cv2.cvtColor(tilted_np, cv2.COLOR_BGRA2RGBA))

    # Vytvoření čtvercového plátna 512x512 s průhledností
    canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
    tilted_w, tilted_h = tilted_image.size

    # Výpočet pozice pro vycentrování
    offset_x = (target_size[0] - tilted_w) // 2
    offset_y = (target_size[1] - tilted_h) // 2

    # Vložení obrázku na čtvercové plátno
    canvas.paste(tilted_image, (offset_x, offset_y), tilted_image)

    # Uložení výsledného obrázku
    canvas.save(f"{i + 2}.png")

print("Hotovo!")
