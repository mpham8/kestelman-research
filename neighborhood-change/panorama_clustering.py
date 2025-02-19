from streetview import search_panoramas
import folium
import numpy as np
from geopy.distance import geodesic

class PanoramaGroupFinder:
    def __init__(self, latitude, longitude, search_grid_diameter_meters, search_grid_nxn, grouping_radius_threshold):
        self.longitude = longitude
        self.latitude = latitude
        self.search_gridcell_meters = search_grid_diameter_meters//search_grid_nxn
        self.search_gridcell_nxn = search_grid_nxn
        self.grouping_radius_threshold = grouping_radius_threshold

    
    def find_nearby(self, lat, lon, lats_ls, lons_ls, panoid_ls):
      panos = search_panoramas(lat=lat, lon=lon)

      for pano in panos[:100]:
          lats_ls.append(pano.lat)
          lons_ls.append(pano.lon)
          panoid_ls.append(pano.pano_id)

      return lats_ls, lons_ls, panoid_ls

    
    def get_all_panos(self):
      lats_ls, lons_ls, panoid_ls = [], [], []


      north = geodesic(meters=self.search_gridcell_meters).destination((self.latitude, self.longitude), 0)
      east = geodesic(meters=self.search_gridcell_meters).destination((self.latitude, self.longitude), 90)
      # calculate grid cell sizes 
      search_grid_lat = north.latitude - self.latitude
      search_grid_lon = east.longitude - self.longitude
      

      for i in range(int(-self.search_gridcell_nxn//2), int(self.search_gridcell_nxn//2) + 1):
        for j in range(int(-self.search_gridcell_nxn//2), int(self.search_gridcell_nxn//2) + 1):
            lat = self.latitude + (i * search_grid_lat)
            lon = self.longitude + (j * search_grid_lon)
            lats_ls, lons_ls, panoid_ls = self.find_nearby(lat, lon, lats_ls, lons_ls, panoid_ls)
      
      return lats_ls, lons_ls, panoid_ls



      # Helper function to calculate distance between two points
    def is_radius(self, lat1, lon1, lat2, lon2, radius_range_meters):
          R = 6371000  # Earth's radius in meters
          lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
          dlat = lat2 - lat1
          dlon = lon2 - lon1
          a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
          c = 2 * np.arcsin(np.sqrt(a))
          return R * c <= radius_range_meters


    
    def create_groupings(self, lats_ls, lons_ls, panoid_ls):
      # Calculate points 3m north and east of center
      north = geodesic(meters=self.grouping_radius_threshold).destination((self.latitude, self.longitude), 0)
      east = geodesic(meters=self.grouping_radius_threshold).destination((self.latitude, self.longitude), 90)

      # Calculate the lat/lon ranges
      radius_range_lat = north.latitude - self.latitude
      radius_range_lon = east.longitude - self.longitude

      lats_sorted = sorted(lats_ls)
      lons_sorted = sorted(lons_ls)
      lat_min, lat_max = lats_sorted[0], lats_sorted[-1]
      lon_min, lon_max = lons_sorted[0], lons_sorted[-1]

      #TEST
      # m = folium.Map(location=[lats_ls[0], lons_ls[0]], zoom_start=16)

      # # Add markers for each point
      # for lat, lon in zip(lats_ls, lons_ls):
      #     folium.Marker([lat, lon]).add_to(m)
      
      # # Save the map to an HTML file
      # m.save("TESTMAP.html")

      lat_grouping_cells = (lat_max - lat_min) // radius_range_lat + 1
      lon_grouping__cells = (lon_max - lon_min) // radius_range_lon + 1
      # lat_cells = side_length_meters // radius_range_meters + 1
      # lon_cells = side_length_meters // radius_range_meters + 1

      # Initialize grid to store points
      grid_points = [[[] for _ in range(int(lon_grouping__cells))] for _ in range(int(lat_grouping_cells))]
      print(f"Grouping grid shape: {len(grid_points)} x {len(grid_points[0])} cells")

      # Categorize points into grid cells
      for lat, lon, panoid in zip(lats_ls, lons_ls, panoid_ls):
          # Calculate grid indices based on relative position
          lat_idx = int((lat - lat_min) // radius_range_lat) 
          lon_idx = int((lon - lon_min) // radius_range_lon)

          grid_points[lat_idx][lon_idx].append([lat, lon, panoid])

    
      # Create lookup dictionary for panoid -> [lon, lat]
      panoid_to_coords_dict = {}
      for lat, lon, panoid in zip(lats_ls, lons_ls, panoid_ls):
          panoid_to_coords_dict[panoid] = [lat, lon]

      # Initialize list to store points and their neighbors within range
      points_with_neighbors = []
      p2c_dict = {} #key: pano id, value: group leader's coordinates [lat, lon]
      grouping_dict = {} #gets the grouping leader's coordinates, key: "lat" +"," + "lon", value: [all pano ids]


      # Iterate through each cell in the grid
      for i in range(len(grid_points)):
          for j in range(len(grid_points[0])):
              # Get points in current cell
              current_points = grid_points[i][j]
              
              # Skip if no points in current cell
              if not current_points:
                  continue
                  
              # Check adjacent cells (including diagonals)
              for di in [-1, 0, 1]:
                  for dj in [-1, 0, 1]:
                      ni, nj = i + di, j + dj
                      
                      # Skip if indices are out of bounds
                      if not (0 <= ni < len(grid_points) and 0 <= nj < len(grid_points[0])):
                          continue
                          
                      # Get points in neighbor cell
                      neighbor_points = grid_points[ni][nj]
                      
                      # For each point in current cell
                      for point1 in current_points:
                          # Compare with each point in neighbor cell
                          for point2 in neighbor_points:
                              # # Skip if same point
                              # if point1 == point2:
                              #     continue
                              p1latlon_str = str(point1[0]) + "," + str(point1[1])
                              p2latlon_str = str(point2[0]) + "," + str(point2[1])

                              if point1[2] in p2c_dict and point2[2] in p2c_dict:
                                  continue
                              if point1[2] == point2[2]:
                                  continue
                              elif point1[2] in p2c_dict:
                                  grouplat, grouplon = p2c_dict[point1[2]]
                                  if self.is_radius(grouplat, grouplon, point2[0], point2[1], self.grouping_radius_threshold):
                                      glatlon_str = str(grouplat) + "," + str(grouplon)
                                      grouping_dict[glatlon_str].append(point2[2])
                                      p2c_dict[point2[2]] = [grouplat, grouplon]
                              elif point2[2] in p2c_dict:
                                  grouplat, grouplon = p2c_dict[point2[2]]
                                  if self.is_radius(point1[0], point1[1], grouplat, grouplon, self.grouping_radius_threshold):
                                      glatlon_str = str(grouplat) + "," + str(grouplon)
                                      grouping_dict[glatlon_str].append(point1[2])
                                      p2c_dict[point1[2]] = [grouplat, grouplon]
                              else:
                                  if self.is_radius(point1[0], point1[1],point2[0], point2[1], self.grouping_radius_threshold):
                                      grouping_dict[p1latlon_str] = [point1[2], point2[2]]
                                      grouplat, grouplon = point1[0], point1[1]
                                      p2c_dict[point1[2]] = [grouplat, grouplon]
                                      p2c_dict[point2[2]] = [grouplat, grouplon]

      # #TEST
      print(f"Number of groups in grouping_dict: {len(grouping_dict)}")
      # Create a base map centered on the first point
      first_group = list(grouping_dict.values())[0]
      first_pano = first_group[0]
      first_coords = panoid_to_coords_dict[first_pano]
      m = folium.Map(location=[first_coords[0], first_coords[1]], zoom_start=15)
      # Generate a list of distinct colors for different groups
      import random
      colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 
                'darkpurple', 'pink', 'lightblue', 'lightgreen']

      # Plot each group with a different color
      for i, (center_str, pano_ids) in enumerate(grouping_dict.items()):
          # Get color for this group (cycle through colors if more groups than colors)
          color = colors[i % len(colors)]
          
          # Create a feature group for this cluster
          group = folium.FeatureGroup(name=f"Group {i}")
          
          # Plot each point in the group
          for pano_id in pano_ids:
              coords = panoid_to_coords_dict[pano_id]
              folium.CircleMarker(
                  location=[coords[0], coords[1]],
                  radius=5,
                  color=color,
                  fill=True,
                  popup=f"Pano ID: {pano_id}",
              ).add_to(group)
          
          # Add the feature group to the map
          group.add_to(m)

      # Add layer control
      folium.LayerControl().add_to(m)

      m.save("TESTMAP2small.html")

      return grouping_dict


    def get_groupings(self):
      lats_ls, lons_ls, panoid_ls = self.get_all_panos()
      grouping_dict = self.create_groupings(lats_ls, lons_ls, panoid_ls)
    #   print(grouping_dict)


      # Save grouping_dict to a Python file
      with open('test_grouping_dict2s.py', 'w') as f:
          f.write('grouping_dict = {\n')
          for key, value in grouping_dict.items():
              f.write(f"    '{key}': {value},\n")
          f.write('}')

PanoramaGroupFinder(latitude = 34.272, longitude= -118.484869, search_grid_diameter_meters = 200, search_grid_nxn = 4, grouping_radius_threshold = 5).get_groupings()