def get_tn(hero_type: str) -> int:
    if hero_type in {"Origin", "Hero"}:
        return 8
    elif hero_type in {"Demigod", "God"}:
        return 7
    elif hero_type == "God Feat of Scale":
        return 6
    else:
        raise ValueError(f"Invalid hero type: {hero_type}")