from PIL import Image
import pygame

def load_image(path, use_alpha=True):
    """Try pygame.image.load; on failure load with Pillow and convert to a
    pygame surface. Returns a Surface (with alpha if use_alpha=True)."""
    try:
        if use_alpha:
            surf = pygame.image.load(path).convert_alpha()
        else:
            surf = pygame.image.load(path).convert()
        print(f"[image_helper] loaded pygame: {path} -> {surf.get_size()}")
        return surf
    except Exception:
        img = Image.open(path)
        mode = 'RGBA' if use_alpha else 'RGB'
        if img.mode != mode:
            img = img.convert(mode)
        data = img.tobytes()
        size = img.size
        surf = pygame.image.frombuffer(data, size, mode)
        if use_alpha:
            out = surf.convert_alpha()
        else:
            out = surf.convert()
        print(f"[image_helper] loaded Pillow fallback: {path} -> {out.get_size()}")
        return out
