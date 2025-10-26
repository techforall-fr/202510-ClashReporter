"""Mock data generation for demo mode."""
import random
import uuid
from datetime import datetime, timedelta
from typing import List

from app.models.clash import Clash, ClashSeverity, ClashStatus, Element, Location


# Realistic BIM data
DISCIPLINES = ["MEP", "Structure", "Architecture", "Plumbing", "Electrical", "HVAC"]
CATEGORIES_MEP = ["Ducts", "Pipes", "Cable Trays", "Conduits", "Air Terminals"]
CATEGORIES_STRUCTURE = ["Beams", "Columns", "Slabs", "Foundations", "Walls"]
CATEGORIES_ARCH = ["Walls", "Doors", "Windows", "Ceilings", "Floors"]
LEVELS = ["L00", "L01", "L02", "L03", "L04", "L05", "Roof"]

CLASH_TITLES = [
    "Duct vs Beam",
    "Pipe vs Column",
    "Cable Tray vs Slab",
    "Conduit vs Wall",
    "Duct vs Structural Beam",
    "Pipe vs Architectural Wall",
    "HVAC vs Structure",
    "Electrical vs MEP",
    "Plumbing vs Structure",
]


def generate_element(discipline: str, category: str = "") -> Element:
    """Generate a mock BIM element."""
    if not category:
        if discipline == "MEP":
            category = random.choice(CATEGORIES_MEP)
        elif discipline == "Structure":
            category = random.choice(CATEGORIES_STRUCTURE)
        else:
            category = random.choice(CATEGORIES_ARCH)
    
    guid = str(uuid.uuid4())
    return Element(
        urn=f"urn:adsk.objects:os.object:demo-bucket/{guid}",
        guid=guid,
        name=f"{category}-{random.randint(1000, 9999)}",
        category=category
    )


def generate_location(level: str) -> Location:
    """Generate a random 3D location."""
    # Typical building coordinates (meters)
    return Location(
        x=round(random.uniform(-50, 50), 2),
        y=round(random.uniform(-50, 50), 2),
        z=round(random.uniform(0, 30), 2),
        level=level
    )


def generate_clash(index: int, base_date: datetime) -> Clash:
    """Generate a single mock clash."""
    clash_id = f"clash_{index:05d}"
    group_id = f"group_{random.randint(1, 20):02d}"
    
    # Select disciplines and categories
    disc_a, disc_b = random.sample(DISCIPLINES[:3], 2)  # Focus on main disciplines
    
    # Random severity with realistic distribution (more medium than high)
    severity_weights = [0.2, 0.5, 0.3]  # high, medium, low
    severity = random.choices(
        [ClashSeverity.HIGH, ClashSeverity.MEDIUM, ClashSeverity.LOW],
        weights=severity_weights
    )[0]
    
    # Status distribution (more open than resolved)
    status_weights = [0.6, 0.3, 0.1]  # open, resolved, suppressed
    status = random.choices(
        [ClashStatus.OPEN, ClashStatus.RESOLVED, ClashStatus.SUPPRESSED],
        weights=status_weights
    )[0]
    
    # Level selection
    level = random.choice(LEVELS)
    
    # Timestamps
    created = base_date - timedelta(days=random.randint(1, 60))
    updated = created + timedelta(days=random.randint(0, 10))
    
    # Title
    title = random.choice(CLASH_TITLES)
    
    return Clash(
        id=clash_id,
        group_id=group_id,
        title=title,
        status=status,
        severity=severity,
        discipline_a=disc_a,
        discipline_b=disc_b,
        element_a=generate_element(disc_a),
        element_b=generate_element(disc_b),
        location=generate_location(level),
        screenshot_url=None,
        acc_link=f"https://acc.autodesk.com/docs/files/projects/mock-project?clash={clash_id}",
        created_at=created,
        updated_at=updated
    )


def generate_mock_clashes(count: int = 100) -> List[Clash]:
    """Generate a set of realistic mock clashes."""
    base_date = datetime.now()
    clashes = [generate_clash(i, base_date) for i in range(count)]
    
    # Sort by severity (high first) then by updated date
    severity_order = {ClashSeverity.HIGH: 0, ClashSeverity.MEDIUM: 1, ClashSeverity.LOW: 2}
    clashes.sort(key=lambda c: (severity_order[c.severity], -c.updated_at.timestamp()))
    
    return clashes


# Generate and cache mock data on module import
_MOCK_CLASHES: List[Clash] = []


def get_mock_clashes(regenerate: bool = False) -> List[Clash]:
    """Get cached mock clashes or regenerate if needed."""
    global _MOCK_CLASHES
    if not _MOCK_CLASHES or regenerate:
        _MOCK_CLASHES = generate_mock_clashes(100)
    return _MOCK_CLASHES


# Public demo URN (Autodesk sample model)
DEMO_URN = "dXJuOmFkc2sub2JqZWN0czpvcy5vYmplY3Q6bW9kZWwyMDIwLTA5LTI0LTA4LTQxLTQxLWQ0MWQ4Y2Q5OGYwMGIyMDRlOTgwMDk5OGVjZjg0MjdlL3JzdGJhc2ljc2FtcGxlcHJvamVjdC5ydnQ"
