import geopandas as gpd
import matplotlib.pyplot as plt

ca = gpd.read_file('path/to/ca_counties.shp')
selected = [
  "Alameda", "Amador", ..., "Yolo"
]
ca['highlight'] = ca['NAME'].isin(selected)

fig, ax = plt.subplots(figsize=(8, 10))
ca.plot(ax=ax, color='lightgrey', edgecolor='white')
ca[ca['highlight']].plot(ax=ax, color='skyblue')
ax.set_axis_off()
plt.show()
