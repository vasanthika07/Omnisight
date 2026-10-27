"""
OmniSight Device Registry
Comprehensive device catalog and dynamic device profile builder.
Supports phones, foldables, tablets, laptops, desktops, ultra-wide monitors,
wearables, and fully custom dynamic device configurations.
"""

from typing import Dict, Any, List, Optional

# Standard Device Presets Catalog
DEVICE_PRESETS: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------
    # PHONES
    # -------------------------------------------------------------
    "iphone_16_pro_max": {
        "id": "iphone_16_pro_max",
        "name": "Apple iPhone 16 Pro Max",
        "category": "phones",
        "width": 440,
        "height": 956,
        "dpr": 3.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1 OmniSight/1.0",
        "safe_area_insets": {"top": 59, "right": 0, "bottom": 34, "left": 0},
        "frame_type": "dynamic_island",
        "description": "6.9\" Super Retina XDR OLED, Dynamic Island"
    },
    "iphone_15_pro": {
        "id": "iphone_15_pro",
        "name": "Apple iPhone 15 Pro",
        "category": "phones",
        "width": 393,
        "height": 852,
        "dpr": 3.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1 OmniSight/1.0",
        "safe_area_insets": {"top": 59, "right": 0, "bottom": 34, "left": 0},
        "frame_type": "dynamic_island",
        "description": "6.1\" Super Retina XDR OLED, Dynamic Island"
    },
    "iphone_14": {
        "id": "iphone_14",
        "name": "Apple iPhone 14",
        "category": "phones",
        "width": 390,
        "height": 844,
        "dpr": 3.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1 OmniSight/1.0",
        "safe_area_insets": {"top": 47, "right": 0, "bottom": 34, "left": 0},
        "frame_type": "notch",
        "description": "6.1\" OLED Display with Classic Sensor Notch"
    },
    "iphone_se": {
        "id": "iphone_se",
        "name": "Apple iPhone SE (Gen 3)",
        "category": "phones",
        "width": 375,
        "height": 667,
        "dpr": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1 OmniSight/1.0",
        "safe_area_insets": {"top": 20, "right": 0, "bottom": 0, "left": 0},
        "frame_type": "classic_bezel",
        "description": "4.7\" Compact LCD with Home Button"
    },
    "galaxy_s24_ultra": {
        "id": "galaxy_s24_ultra",
        "name": "Samsung Galaxy S24 Ultra",
        "category": "phones",
        "width": 412,
        "height": 915,
        "dpr": 3.5,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.113 Mobile Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 36, "right": 0, "bottom": 16, "left": 0},
        "frame_type": "punch_hole",
        "description": "6.8\" Dynamic AMOLED 2X, Punch-hole Camera"
    },
    "pixel_8_pro": {
        "id": "pixel_8_pro",
        "name": "Google Pixel 8 Pro",
        "category": "phones",
        "width": 448,
        "height": 998,
        "dpr": 2.8,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 36, "right": 0, "bottom": 16, "left": 0},
        "frame_type": "punch_hole",
        "description": "6.7\" Super Actua Display, Android 14"
    },

    # -------------------------------------------------------------
    # FOLDABLES
    # -------------------------------------------------------------
    "galaxy_z_fold5_cover": {
        "id": "galaxy_z_fold5_cover",
        "name": "Galaxy Z Fold 5 (Cover Screen)",
        "category": "foldables",
        "width": 375,
        "height": 904,
        "dpr": 2.625,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 32, "right": 0, "bottom": 16, "left": 0},
        "frame_type": "tall_foldable",
        "description": "6.2\" Ultra-tall Narrow Outer Aspect Ratio (23.1:9)"
    },
    "galaxy_z_fold5_unfolded": {
        "id": "galaxy_z_fold5_unfolded",
        "name": "Galaxy Z Fold 5 (Unfolded Inner Display)",
        "category": "foldables",
        "width": 816,
        "height": 1016,
        "dpr": 2.625,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 32, "right": 0, "bottom": 16, "left": 0},
        "frame_type": "square_tablet",
        "description": "7.6\" Near-Square Dual-Screen Inner Foldable Canvas"
    },
    "pixel_fold_unfolded": {
        "id": "pixel_fold_unfolded",
        "name": "Google Pixel Fold (Inner Landscape)",
        "category": "foldables",
        "width": 892,
        "height": 702,
        "dpr": 2.625,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "landscape",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel Fold) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 24, "right": 0, "bottom": 16, "left": 0},
        "frame_type": "landscape_foldable",
        "description": "7.6\" Wide-aspect Inner Folding Display"
    },

    # -------------------------------------------------------------
    # TABLETS
    # -------------------------------------------------------------
    "ipad_pro_12_9": {
        "id": "ipad_pro_12_9",
        "name": "Apple iPad Pro 12.9\"",
        "category": "tablets",
        "width": 1024,
        "height": 1366,
        "dpr": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1 OmniSight/1.0",
        "safe_area_insets": {"top": 24, "right": 0, "bottom": 20, "left": 0},
        "frame_type": "tablet_bezel",
        "description": "12.9\" Liquid Retina XDR Mini-LED, iPadOS"
    },
    "ipad_air": {
        "id": "ipad_air",
        "name": "Apple iPad Air 11\"",
        "category": "tablets",
        "width": 820,
        "height": 1180,
        "dpr": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1 OmniSight/1.0",
        "safe_area_insets": {"top": 24, "right": 0, "bottom": 20, "left": 0},
        "frame_type": "tablet_bezel",
        "description": "10.9\" Liquid Retina Display, iPadOS"
    },
    "ipad_mini": {
        "id": "ipad_mini",
        "name": "Apple iPad Mini",
        "category": "tablets",
        "width": 744,
        "height": 1133,
        "dpr": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1 OmniSight/1.0",
        "safe_area_insets": {"top": 24, "right": 0, "bottom": 20, "left": 0},
        "frame_type": "tablet_bezel",
        "description": "8.3\" Liquid Retina Ultra-Compact Tablet"
    },
    "galaxy_tab_s9": {
        "id": "galaxy_tab_s9",
        "name": "Samsung Galaxy Tab S9 Ultra",
        "category": "tablets",
        "width": 1120,
        "height": 1792,
        "dpr": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-X910) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 24, "right": 0, "bottom": 16, "left": 0},
        "frame_type": "tablet_bezel",
        "description": "14.6\" Dynamic AMOLED 2X, Android Tablet"
    },

    # -------------------------------------------------------------
    # LAPTOPS & DESKTOPS
    # -------------------------------------------------------------
    "macbook_air_13": {
        "id": "macbook_air_13",
        "name": "Apple MacBook Air 13\" (M3)",
        "category": "desktops",
        "width": 1280,
        "height": 832,
        "dpr": 2.0,
        "is_mobile": False,
        "has_touch": False,
        "orientation": "landscape",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 32, "right": 0, "bottom": 0, "left": 0},
        "frame_type": "laptop_notch",
        "description": "13.6\" Liquid Retina with Camera Notch"
    },
    "macbook_pro_16": {
        "id": "macbook_pro_16",
        "name": "Apple MacBook Pro 16\" (M3 Max)",
        "category": "desktops",
        "width": 1728,
        "height": 1117,
        "dpr": 2.0,
        "is_mobile": False,
        "has_touch": False,
        "orientation": "landscape",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 32, "right": 0, "bottom": 0, "left": 0},
        "frame_type": "laptop_notch",
        "description": "16.2\" Liquid Retina XDR 120Hz ProMotion"
    },
    "desktop_1080p": {
        "id": "desktop_1080p",
        "name": "Full HD Standard Desktop (1080p)",
        "category": "desktops",
        "width": 1920,
        "height": 1080,
        "dpr": 1.0,
        "is_mobile": False,
        "has_touch": False,
        "orientation": "landscape",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 0, "right": 0, "bottom": 0, "left": 0},
        "frame_type": "desktop_monitor",
        "description": "1920×1080 Full HD Workstation Standard"
    },
    "desktop_2k_qhd": {
        "id": "desktop_2k_qhd",
        "name": "QHD 2K Monitor (1440p)",
        "category": "desktops",
        "width": 2560,
        "height": 1440,
        "dpr": 1.0,
        "is_mobile": False,
        "has_touch": False,
        "orientation": "landscape",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 0, "right": 0, "bottom": 0, "left": 0},
        "frame_type": "desktop_monitor",
        "description": "2560×1440 High-Density Gaming & Developer Display"
    },
    "desktop_4k_uhd": {
        "id": "desktop_4k_uhd",
        "name": "Ultra HD 4K Display (2160p)",
        "category": "desktops",
        "width": 3840,
        "height": 2160,
        "dpr": 1.5,
        "is_mobile": False,
        "has_touch": False,
        "orientation": "landscape",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 0, "right": 0, "bottom": 0, "left": 0},
        "frame_type": "desktop_monitor",
        "description": "3840×2160 4K UHD Ultra-High Density Canvas"
    },
    "desktop_ultrawide": {
        "id": "desktop_ultrawide",
        "name": "Curved Ultrawide 21:9 (UWQHD)",
        "category": "desktops",
        "width": 3440,
        "height": 1440,
        "dpr": 1.0,
        "is_mobile": False,
        "has_touch": False,
        "orientation": "landscape",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 0, "right": 0, "bottom": 0, "left": 0},
        "frame_type": "ultrawide_monitor",
        "description": "3440×1440 Panoramic 21:9 Aspect Ratio Display"
    },

    # -------------------------------------------------------------
    # WEARABLES & EMBEDDED KIOSKS
    # -------------------------------------------------------------
    "apple_watch_45mm": {
        "id": "apple_watch_45mm",
        "name": "Apple Watch Series 9 (45mm)",
        "category": "wearables",
        "width": 198,
        "height": 242,
        "dpr": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "orientation": "portrait",
        "user_agent": "Mozilla/5.0 (Apple-Watch; CPU WatchOS 10_0 like Mac OS X) AppleWebKit/605.1.15 OmniSight/1.0",
        "safe_area_insets": {"top": 12, "right": 8, "bottom": 12, "left": 8},
        "frame_type": "watch_rounded",
        "description": "1.9\" Micro-OLED Wearable Canvas (Edge Extreme)"
    },
    "kiosk_pos_terminal": {
        "id": "kiosk_pos_terminal",
        "name": "Retail POS Touch Kiosk",
        "category": "wearables",
        "width": 1024,
        "height": 768,
        "dpr": 1.0,
        "is_mobile": False,
        "has_touch": True,
        "orientation": "landscape",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OmniSight/1.0",
        "safe_area_insets": {"top": 0, "right": 0, "bottom": 0, "left": 0},
        "frame_type": "kiosk_terminal",
        "description": "15\" 4:3 Commercial Touchscreen Terminal"
    }
}

DEVICE_CATEGORIES = [
    {"id": "all", "name": "All Devices", "icon": "Layers"},
    {"id": "phones", "name": "Smartphones", "icon": "Smartphone"},
    {"id": "foldables", "name": "Foldables & Dual Screen", "icon": "BookOpen"},
    {"id": "tablets", "name": "Tablets & iPads", "icon": "Tablet"},
    {"id": "desktops", "name": "Laptops & Ultrawide", "icon": "Monitor"},
    {"id": "wearables", "name": "Wearables & Kiosks", "icon": "Watch"},
    {"id": "custom", "name": "Custom Dynamic Device", "icon": "Sliders"}
]

def get_all_devices() -> List[Dict[str, Any]]:
    """Returns all standard device presets as an ordered list."""
    return list(DEVICE_PRESETS.values())

def get_device_by_id(device_id: str) -> Dict[str, Any]:
    """Retrieves a specific device configuration by its ID, with safe fallback."""
    if device_id in DEVICE_PRESETS:
        return dict(DEVICE_PRESETS[device_id])
    return dict(DEVICE_PRESETS["iphone_15_pro"])

def create_custom_device(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamically creates or validates a custom device configuration.
    Supports flipping orientation, custom DPR, touch emulation, safe areas, etc.
    """
    width = int(spec.get("width", 393))
    height = int(spec.get("height", 852))
    orientation = str(spec.get("orientation", "portrait")).lower()
    
    # Auto-adjust dimensions if orientation flip was requested
    if orientation == "landscape" and width < height:
        width, height = height, width
    elif orientation == "portrait" and width > height:
        width, height = height, width

    dpr = float(spec.get("dpr", 2.0))
    is_mobile = bool(spec.get("is_mobile", width <= 768))
    has_touch = bool(spec.get("has_touch", width <= 1024))
    
    user_agent = spec.get("user_agent")
    if not user_agent:
        if is_mobile:
            user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1 OmniSight/1.0"
        else:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0"

    safe_area = spec.get("safe_area_insets") or {"top": 0, "right": 0, "bottom": 0, "left": 0}

    return {
        "id": spec.get("id", f"custom_{width}x{height}"),
        "name": spec.get("name", f"Custom Device ({width}×{height} @{dpr}x)"),
        "category": "custom",
        "width": width,
        "height": height,
        "dpr": dpr,
        "is_mobile": is_mobile,
        "has_touch": has_touch,
        "orientation": orientation,
        "user_agent": user_agent,
        "safe_area_insets": safe_area,
        "frame_type": spec.get("frame_type", "custom_frame"),
        "description": f"Dynamically synthesized custom profile: {width}×{height}px, DPR {dpr}x, {orientation.upper()}"
    }
