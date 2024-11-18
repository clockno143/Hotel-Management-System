import folium
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Create a map centered at a specific location
folium.CircleMarker(
    location=[45.5236, -122.6750],

    radius=50,
    popup='Circle Marker',
    color='red',
    fill=True,
    fill_color='red'
).add_to(m)
# Save the map to an HTML file
m.save('map.html')