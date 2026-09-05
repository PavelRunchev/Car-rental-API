
# ==========================
# AUTH
# ==========================
def normalize_email(email: str) -> str:
    return email.strip().lower()

def normalize_name(name: str) -> str:
    return name.strip()

def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None

    return (phone.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", ""))

# ==========================
# BRAND
# ==========================
def normalize_brand_name(name: str) -> str:
    return name.strip()

# ==========================
# MODEL
# ==========================
def normalize_model_name(name: str) -> str:
    return name.strip()

# ==========================
# CATEGORY
# ==========================
def normalize_category_name(name: str) -> str:
    return name.strip()

# ==========================
# CAR
# ==========================
def normalize_license_plate(name: str) -> str:
    return name.strip()

def normalize_color(name: str) -> str:
    return name.strip()