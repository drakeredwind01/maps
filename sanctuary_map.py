
# ---------------------------------------------------------------------------
# VISUALIZATION  (matplotlib static — lonboard coming next phase)
# ---------------------------------------------------------------------------

ZONE_STYLES = {
    "freeway_zone": dict(color="#e74c3c", alpha=0.35, label=f"Freeway exclusion ({BUFFERS['freeway']}m / ~2,000 ft)"),
    "airport_zone": dict(color="#e67e22", alpha=0.25, label=f"Airport exclusion ({BUFFERS['airport']}m / ~5 mi)"),
    "river_zone":   dict(color="#2980b9", alpha=0.40, label=f"River/flood corridor ({BUFFERS['river']}m)"),
}


def plot_map(
    study_bbox: dict,
    features:   dict,
    zones:      dict,
    safe_zone:  gpd.GeoDataFrame,
    output_path: Path,
) -> None:
    """Render and save the exclusion + safe zone map as a PNG."""

    print("\n  Rendering map...")

    fig, ax = plt.subplots(figsize=(14, 14))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")

    # Study area outline
    study_poly = gpd.GeoDataFrame(
        geometry=[bbox_polygon(study_bbox)], crs=CRS_WGS84
    )
    study_poly.plot(ax=ax, color="#0f3460", edgecolor="#e0e0e0", linewidth=1.5)

    # Safe zone (green)
    if not safe_zone.empty:
        safe_zone.plot(ax=ax, color="#27ae60", alpha=0.25, label="Potential safe areas")

    # Exclusion zones
    for zone_name, gdf in zones.items():
        style = ZONE_STYLES.get(zone_name, {})
        gdf.plot(ax=ax, color=style["color"], alpha=style["alpha"])

    # Raw features (subtle)
    if not features["freeways"].empty:
        features["freeways"].plot(ax=ax, color="#c0392b", linewidth=0.6, alpha=0.5)
    if not features["rivers"].empty:
        features["rivers"].plot(ax=ax, color="#3498db", linewidth=0.6, alpha=0.5)

    # Legend
    legend_patches = [
        mpatches.Patch(color="#27ae60", alpha=0.5, label="Potential safe areas"),
    ]
    for zone_name, style in ZONE_STYLES.items():
        if zone_name in zones:
            legend_patches.append(
                mpatches.Patch(color=style["color"], alpha=0.7, label=style["label"])
            )

    ax.legend(
        handles=legend_patches,
        loc="lower right",
        facecolor="#0f3460",
        edgecolor="#e0e0e0",
        labelcolor="white",
        fontsize=9,
    )

    ax.set_xlim(study_bbox["west"], study_bbox["east"])
    ax.set_ylim(study_bbox["south"], study_bbox["north"])
    ax.set_title(
        "Sanctuary Map — San Diego County\nHealth-Based Residential Exclusion Zones",
        color="white",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Longitude", color="#aaaaaa")
    ax.set_ylabel("Latitude",  color="#aaaaaa")
    ax.tick_params(colors="#aaaaaa")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444466")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor())
    print(f"  Map saved → {output_path.resolve()}")
    plt.show()


# ---------------------------------------------------------------------------
# SAVE OUTPUTS
# ---------------------------------------------------------------------------

def save_outputs(safe_zone: gpd.GeoDataFrame, zones: dict) -> None:
    """Save safe zone and exclusion zones to GeoPackage for GIS use."""
    print("\n  Saving vector outputs...")

    safe_zone.to_file(OUTPUT_SAFE_SHP, layer="safe_zones", driver="GPKG")

    for zone_name, gdf in zones.items():
        gdf.to_file(OUTPUT_SAFE_SHP, layer=zone_name, driver="GPKG")

    print(f"  GeoPackage saved → {OUTPUT_SAFE_SHP.resolve()}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Sanctuary Map — health-based residential zone finder for San Diego, CA"
    )
    parser.add_argument(
        "--bbox",
        type=str,
        default=None,
        help='Bounding box as "south,north,west,east" — default is full SD County',
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Skip saving GeoPackage outputs (map PNG is always saved)",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("  SANCTUARY MAP  —  San Diego Health Zone Finder")
    print("=" * 60)

    args = parse_args()

    # Resolve bounding box
    bbox = DEFAULT_BBOX.copy()
    if args.bbox:
        try:
            s, n, w, e = [float(v.strip()) for v in args.bbox.split(",")]
            bbox = {"south": s, "north": n, "west": w, "east": e}
            print(f"\n  Custom bbox: S={s} N={n} W={w} E={e}")
        except ValueError:
            print("  ERROR: --bbox must be 'south,north,west,east'")
            sys.exit(1)
    else:
        print(f"\n  Using default bbox: full San Diego County")

    # Validate PBF
    check_pbf(PBF_FILE)

    # Study area polygon
    study_area = gpd.GeoDataFrame(
        geometry=[bbox_polygon(bbox)], crs=CRS_WGS84
    )

    # Extract → buffer → compute safe zone → visualize
    features  = extract_features(PBF_FILE, bbox)
    zones     = build_exclusion_zones(features)
    safe_zone = build_safe_zone(zones, study_area)

    # Report
    study_area_m2 = study_area.to_crs(CRS_METRIC).geometry.iloc[0].area
    safe_area_m2  = safe_zone.to_crs(CRS_METRIC).geometry.iloc[0].area if not safe_zone.empty else 0
    pct_safe      = (safe_area_m2 / study_area_m2) * 100 if study_area_m2 > 0 else 0

    print(f"\n  Study area  : {study_area_m2 / 1_000_000:.1f} km²")
    print(f"  Safe area   : {safe_area_m2  / 1_000_000:.1f} km²")
    print(f"  % livable   : {pct_safe:.1f}%")

    # Outputs
    plot_map(bbox, features, zones, safe_zone, OUTPUT_MAP_PNG)

    if not args.no_save:
        save_outputs(safe_zone, zones)

    print("\n  Done.\n")


if __name__ == "__main__":
    main()
