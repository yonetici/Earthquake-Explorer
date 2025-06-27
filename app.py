"""
Earthquake Explorer: Interactive Earthquake Data Viewer (USGS API)
==================================================================
Author: Ridvan BİLGİN
Date: 2025-06-25

Description:
------------
This Streamlit app lets users visually query and analyze recent earthquakes using the USGS Earthquake API.
Features include:

- Magnitude and date range filters.
- Interactive map for polygon-based region selection (draw/edit/delete polygons).
- Results table with sortable columns (time, magnitude, depth, location, coordinates, detail link).
- Optional CSV/Excel export.
- Basic statistics in the sidebar.

Setup:
------
1. Install dependencies:
   pip install -r requirements.txt

2. Run the app:
   streamlit run app.py

Manual Test Cases:
------------------
1. Mag ≥ 6, 2023-02-02 to 2023-03-03, polygon covering Turkey.
2. Mag ≥ 7, worldwide, last 30 days.

Notes:
------
- No API key required.
- USGS API Docs: https://earthquake.usgs.gov/fdsnws/event/1/
- If multiple polygons are drawn, only earthquakes inside at least one polygon are shown.
"""

import streamlit as st
from streamlit_folium import st_folium
import folium
import io
from folium.plugins import Draw
import pandas as pd
import requests
from shapely.geometry import shape, Point
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

def fetch_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch earthquake data from USGS API with given parameters."""
    try:
        resp = requests.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API request failed: {e}")
        return {}

def normalize_data(geojson: Dict[str, Any]) -> pd.DataFrame:
    """Normalize GeoJSON features to pandas DataFrame and process columns."""
    if not geojson or "features" not in geojson or not geojson["features"]:
        return pd.DataFrame()
    df = pd.json_normalize(geojson["features"])
    df = df.rename(columns={
        'properties.time': 'time_epoch',
        'properties.mag': 'magnitude',
        'properties.place': 'place',
        'geometry.coordinates': 'coordinates',
        'properties.depth': 'depth_km',
        'properties.alert': 'alert_level',
        'properties.url': 'url',
    })
    # Time conversion and flatten coordinates
    df['time_utc'] = pd.to_datetime(df['time_epoch'], unit='ms', utc=True)
    df['longitude'] = df['coordinates'].apply(lambda x: x[0])
    df['latitude'] = df['coordinates'].apply(lambda x: x[1])
    df['depth_km'] = df['coordinates'].apply(lambda x: x[2] if len(x) > 2 else None)
    # Create clickable link for USGS event
    df['details'] = df.apply(lambda row: f'<a href="{row["url"]}" target="_blank">Detail</a>', axis=1)
    cols = ['time_utc', 'magnitude', 'place', 'latitude', 'longitude', 'depth_km', 'alert_level', 'url', 'details']
    cols = [c for c in cols if c in df.columns]  # Select only present columns
    return df[cols]

def filter_with_polygons(df: pd.DataFrame, polygons: List[Dict]) -> pd.DataFrame:
    """Filter DataFrame rows to those inside any drawn polygon."""
    if not polygons or df.empty:
        return df
    shapes = [shape(poly['geometry']) for poly in polygons if 'geometry' in poly]
    def inside_any_poly(lat, lon):
        pt = Point(lon, lat)
        return any(poly.contains(pt) for poly in shapes)
    mask = df.apply(lambda row: inside_any_poly(row['latitude'], row['longitude']), axis=1)
    return df[mask]

def get_bounding_box(polygons: List[Dict]) -> Optional[Dict[str, float]]:
    """Compute overall bounding box from multiple polygons (min/max lat/lon)."""
    if not polygons:
        return None
    lats, lons = [], []
    for poly in polygons:
        try:
            coords = []
            # Polygon or MultiPolygon
            geom = poly['geometry']
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
            elif geom['type'] == 'MultiPolygon':
                for sub in geom['coordinates']:
                    coords.extend(sub[0])
            for lon, lat in coords:
                lats.append(lat)
                lons.append(lon)
        except Exception:
            continue
    if not lats or not lons:
        return None
    return {
        'minlatitude': min(lats),
        'maxlatitude': max(lats),
        'minlongitude': min(lons),
        'maxlongitude': max(lons)
    }

def build_map(polygons: Optional[List[Dict]], earthquakes_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """Build Folium map with drawing controls and earthquake markers."""
    m = folium.Map(location=[39, 35], zoom_start=2, control_scale=True)

    # Draw controls
    draw = Draw(
        export=True,
        filename='polygons.geojson',
        draw_options={
            'polyline': False,
            'rectangle': True,
            'polygon': True,
            'circle': False,
            'marker': False,
            'circlemarker': False,
        },
        edit_options={'edit': True, 'remove': True}
    )
    draw.add_to(m)

    # Existing polygons
    if polygons:
        for poly in polygons:
            folium.GeoJson(poly).add_to(m)

    # Earthquake markers
    if earthquakes_df is not None and not earthquakes_df.empty:
        for _, row in earthquakes_df.iterrows():
            popup = folium.Popup(
                f"<b>{row['place']}</b><br>Magnitude: {row['magnitude']}<br><a href='{row['url']}' target='_blank'>Details</a>",
                max_width=300
            )
            folium.CircleMarker(
                location=(row['latitude'], row['longitude']),
                radius=4 + row['magnitude'],
                color="red",
                fill=True,
                fill_opacity=0.7,
                popup=popup
            ).add_to(m)

    return st_folium(m, height=500, width=800, returned_objects=['all_drawings'])

def main():
    st.set_page_config("Earthquake Explorer", "🌍", layout="wide")
    st.title("🌍 Earthquake Explorer — USGS API Interactive Viewer")

    # Sidebar: Filters
    st.sidebar.header("🔎 Query Filters")
    today = datetime.now(timezone.utc).date()
    default_start = today - timedelta(days=2)
    default_end = today
    # Use session_state for inputs so filters persist
    if "start_date" not in st.session_state:
        st.session_state.start_date = default_start
    if "end_date" not in st.session_state:
        st.session_state.end_date = default_end
    if "minmag" not in st.session_state:
        st.session_state.minmag = 6.0
    if "maxmag" not in st.session_state:
        st.session_state.maxmag = 9.0

    start_date = st.sidebar.date_input("Start date", st.session_state.start_date, key="start_date")
    end_date = st.sidebar.date_input("End date", st.session_state.end_date, key="end_date")
    minmag, maxmag = st.sidebar.slider("Magnitude range", 0.0, 10.0, (st.session_state.minmag, st.session_state.maxmag), 0.1, key="mag_range")
    orderby = st.sidebar.selectbox("Order by", ["time", "magnitude", "time-asc", "magnitude-asc"])
    alertlevel = st.sidebar.selectbox("Alert level", ["", "green", "yellow", "orange", "red"])

    st.sidebar.markdown("**Location filter:** Draw one or more polygons or rectangles on the map below.")

    # Map drawing widget
    st.subheader("1. Select region (draw polygons/rectangles)")
    map_result = build_map(None, None)
    polygons = map_result.get('all_drawings', [])

    st.subheader("2. Set filters & click to list earthquakes")
    query = st.button("List Earthquakes")

    # State: Track if initial query has run
    if "run_query" not in st.session_state:
        st.session_state.run_query = False

    df = pd.DataFrame()

    # Run query if (button pressed) or (first load, and not yet queried)
    if query or not st.session_state.run_query:
        with st.spinner("Fetching data from USGS..."):
            params = {
                "format": "geojson",
                "starttime": start_date.isoformat(),
                "endtime": end_date.isoformat(),
                "minmagnitude": minmag,
                "maxmagnitude": maxmag,
                "orderby": orderby,
                "limit": 20000,   # USGS API cap; tune as needed
            }
            if alertlevel:
                params["alertlevel"] = alertlevel
            bbox = get_bounding_box(polygons)
            if bbox:
                params.update(bbox)
            geojson = fetch_data(params)
            df = normalize_data(geojson)
            # Polygon strict filtering (after bbox) if needed
            if polygons:
                df = filter_with_polygons(df, polygons)
        st.session_state.run_query = True
        st.session_state.df = df
    else:
        df = st.session_state.get("df", pd.DataFrame())

    # Display results
    if not df.empty:
        st.subheader("3. Earthquake Map with Markers")
        build_map(polygons, df)
        # Show with clickable HTML links
        styled_df = df.copy()
        styled_df['place'] = styled_df.apply(
            lambda row: f'<a href="{row["url"]}" target="_blank">{row["place"]}</a>'
            if pd.notna(row.get("place")) and pd.notna(row.get("url", None)) else (row.get("place", "") or ""), axis=1
        )

        # Only show columns for display
        display_cols = ['time_utc', 'magnitude', 'place', 'latitude', 'longitude', 'depth_km', 'alert_level', 'details']
        st.markdown(
            styled_df[display_cols].to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
        with st.expander("Download results"):
            st.download_button("Export as CSV", data=styled_df.to_csv(index=False), file_name="earthquakes.csv", mime="text/csv")
            # Remove timezone info for Excel
            if "time_utc" in styled_df.columns:
                styled_df["time_utc"] = styled_df["time_utc"].dt.tz_localize(None)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                styled_df.to_excel(writer, index=False)
            st.download_button(
                "Export as Excel",
                data=output.getvalue(),
                file_name="earthquakes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        # Stats
        st.sidebar.markdown("## 📊 Stats")
        st.sidebar.write(f"Total quakes: **{len(df)}**")
        st.sidebar.write(f"Mean magnitude: **{df['magnitude'].mean():.2f}**")
        st.sidebar.write(f"Deepest: **{df['depth_km'].max():.1f} km**")
        st.sidebar.write(f"Largest: **{df['magnitude'].max():.1f}**")
    elif st.session_state.run_query:
        st.warning("No earthquakes found with the selected filters.")

    # Footer
    st.markdown("""
        <small>
        Data source: <a href="https://earthquake.usgs.gov/fdsnws/event/1/" target="_blank">USGS Earthquake API</a>.<br>
        App by  <a href="https://www.linkedin.com/in/ridvan-bilgin/" target="_blank">Ridvan Bilgin</a>. 2025.
        </small>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
