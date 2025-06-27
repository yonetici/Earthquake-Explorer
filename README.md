# Earthquake-Explorer

**Earthquake-Explorer** is an interactive, open-source web application to visualize, filter, and analyze recent earthquakes worldwide using the USGS Earthquake API.  
It provides a user-friendly web interface to search, map, and export seismic events based on your own criteria.

---

## 🌍 Features

- Real-time earthquake listing and interactive visualization on a world map  
- Filter by date range and minimum/maximum magnitude  
- Draw polygons or rectangles on the map to select geographic regions of interest  
- Sortable, clickable results table with direct links to USGS event details  
- Download filtered results as CSV or Excel file  
- Sidebar displays key statistics (total quakes, mean magnitude, deepest/largest events)  
- No API key or registration required  
- Open source, easy to deploy and customize

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/Earthquake-Explorer.git
cd Earthquake-Explorer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

Open your browser and visit [http://localhost:8501](http://localhost:8501).

---

## 📖 Usage

- Set the date range and minimum/maximum magnitude in the sidebar.  
- Draw one or more polygons or rectangles on the interactive map to filter by region.  
- Click **List Earthquakes** to retrieve and view earthquakes matching your criteria.  
- Results are displayed in a sortable table. Each location links to detailed information on the USGS website.  
- Export the filtered data as CSV or Excel for further analysis.  
- The sidebar displays statistics such as total earthquakes, average magnitude, and maximum depth.

#### Example Test Cases

- Show all earthquakes with magnitude ≥ 6 between 2023-02-02 and 2023-03-03 using a polygon covering Turkey.  
- List all earthquakes with magnitude ≥ 7 worldwide in the last 30 days.

---

## 📦 Requirements

- Python 3.8 or newer  
- See `requirements.txt` for all Python dependencies:
  - streamlit  
  - streamlit-folium  
  - folium  
  - pandas  
  - requests  
  - shapely  
  - openpyxl  

---

## 🗺 Data Source

- [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/)  
- Data is provided under US public domain.

---

## 📝 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.

---

## 💡 Contributing

Contributions are welcome!  
If you want to submit a feature, bugfix, or documentation improvement, please open an issue first to discuss your idea before submitting a pull request.

---

## 📬 Contact

- Author: Ridvan Bilgin  
- LinkedIn: [https://www.linkedin.com/in/ridvan-bilgin/](https://www.linkedin.com/in/ridvan-bilgin/)
- GitHub: [https://github.com/yonetici/Earthquake-Explorer](https://github.com/yonetici/Earthquake-Explorer)

---

## Project Description

Earthquake-Explorer enables researchers, emergency planners, educators, and the public to monitor and analyze seismic activity globally.  
With its interactive mapping and rich filtering options, you can explore earthquake events anywhere in the world, examine their properties in detail, and easily export data for reporting or further study.  
No authentication, payment, or setup beyond installing Python dependencies is required.  
Feel free to modify and extend the application for your needs!

---
