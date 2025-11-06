"""
This script contains custom functions used to show the maps

"""

# Display Synthetic Population Map
import geopandas as gpd
import folium
from src.cases import VAR_CODE_CENSUS_2021_SIMPLIFIED
from src.config import RES_SYN_POP_PATH, RES_MAP_PATH

# Define Helper functions
# Input
def map_age_index(i): return ['child', 'young_adult', 'adult', 'senior'][i]
def map_gender_index(i): return ['female', 'male'][i]
def map_marital_status_index(i): return ['single', 'married', 'divorced_widowed'][i]
def map_eco_act_index(i): return ['employed', 'unemployed', 'inactive'][i]
def map_ethnic_index(i): return ['asian', 'black', 'mixed', 'white', 'other'][i]
def map_cars_index(i): return ['none', 'one', 'two', 'three_or_more'][i]
def map_grade_index(i): return ['ab', 'c1', 'c2', 'de'][i]

# output
def map_product(i): return ['Cloth & Personal Care', 'High-Value Electronics', 
                            'Consumer Goods', 'Entertainment Products', 
                            'Medium-Sized Durable Home Goods','Large Heavy Items','Travel & Luggage Product'][i]
def map_frequency(i): return ['multi_daily', 'daily', 'weekly_2_3_times', 'weekly_once', 
                              'monthly_2_3_times', 'monthly_once', 'yearly_multi', 'less_than_year'][i]

def show_syn_population_map(
    gpkg_name: str,
    sample_rate: float = 0.05,
    map_name: str = "synthetic_population_map.html",
    syn_size: int = 1e5,
    map_location: list = None,
    zoom_start: int = 12,
):
    """
    Visualize point-based population data from a shapefile on an interactive map using folium.
    Supports downsampling to reduce clutter.

    Parameters:
        gpkg_name (str): Name of the synthetic population gpkg file with suffix(.gpkg), containing point data.
        sample_rate (float): Proportion of population points to display (e.g., 0.05 = 5%).
        map_location (list): Initial center of the map [latitude, longitude]. 
                             If None, the center is auto-calculated from data.
        zoom_start (int): Initial zoom level of the map.
        save_path (str): Output HTML file name to save the interactive map.
    """
    # Load the shapefile using geopandas
    gdf = gpd.read_file(RES_SYN_POP_PATH / gpkg_name, layer='syn_pop')
    gdf = gdf.to_crs(epsg=4326)

    popup_attrs_show_dict = {
        'age': 'Age', 
        'sex': "Sex", 
        'ethnic_group': 'Ethnic Group', 
        'economic_activity': 'Economic Activity Status', 
        'number_of_cars_and_vans': 'Number of Cars/Vans', 
        'marital_status': 'Martial Status',
    }
    # ori_name_dic = {'age':'age', 'sex':'sex', 'ethnic_gro':'ethnic_group', 'economic_a':'economic_activity', 'number_of_':'number_of_cars_and_vans', 'marital_st':'marital_status', }
    ori_name_list = ['age', 'sex', 'ethnic_group', 'economic_activity', 'number_of_cars_and_vans', 'marital_status']

    # Filter for point geometries only (skip lines or polygons if any)
    gdf = gdf[gdf.geometry.type == 'Point']
    
    # Perform random sampling (without replacement)
    sample_size = int(len(gdf) * sample_rate)
    sampled_gdf = gdf.sample(n=sample_size, random_state=42)
    
    # Determine map center if not provided
    if map_location is None:
        center = sampled_gdf.geometry.union_all().centroid
        map_location = [center.y, center.x]
    
    # Create the base folium map
    fmap = folium.Map(location=map_location, zoom_start=zoom_start)
    
    # Add sampled points to the map
    for _, row in sampled_gdf.iterrows():
        lon, lat = row.geometry.x, row.geometry.y

        # Create custom popup - set size, font, width, etc
        popup_html = "<div style='font-size:12px; line-height:1.5; font-family:Arial;'>"
        for col in ori_name_list:
            label = popup_attrs_show_dict[col]
            value = VAR_CODE_CENSUS_2021_SIMPLIFIED[col][row[col]]
            popup_html += f"<b>{label}:</b> {value}<br>"
        popup_html += "</div>"

        popup = folium.Popup(popup_html, max_width=300)
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color='red',
            fill=True,
            fill_opacity=1,
            popup=popup
        ).add_to(fmap)

    # Add comment bar
    population_features = {
        'Age': '0-100',
        'Sex': 'Male/Female',
        'Ethnic Group': 'Various',
        'Economic Activity': 'Employed/Unemployed/Inactive', 
        'Number of Cars': '0-3+', 
        'Martial Status': 'Single/Married/Divorced',
    }

    info_html = '''
    <div style="
        position: fixed;
        bottom: 25px;
        left: 30px;
        width: 240px;
        max-height: 350px;
        border: 2px solid grey;
        background-color: white;
        padding: 10px;
        font-size: 14px;
        z-index: 9999;
        overflow-y: auto;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    ">
        <b style="font-size:16px;">Synthetic Population</b><br>
        <b>Population Size:</b> {total_population:,.0f}<br>
        <b>Display Sample Rate:</b> {sample_rate:.1%}<br>
        <b>Population Features:</b><br>
        <ul style="margin-top:0; padding-left: 18px;">
    '''.format(total_population=syn_size, sample_rate=sample_rate)

    for feat_name, feat_desc in population_features.items():
        info_html += f'<li><b>{feat_name}:</b> {feat_desc}</li>'

    info_html += '''
        </ul>
    </div>
    '''

    fmap.get_root().html.add_child(folium.Element(info_html))

    # Save the final interactive map to an HTML file
    fmap.save(RES_MAP_PATH / f'{map_name}')
    print(f"Map successfully saved to: {RES_MAP_PATH / f'{map_name}'}")


# Display Synthetic Order Map
import geopandas as gpd
import folium
import seaborn as sns
import matplotlib.colors as mcolors

def show_syn_orders_map(
    shp_path: str,
    sample_rate: float = 0.05,
    map_location: list = None,
    zoom_start: int = 12,
    save_path = None
):
    """
    Visualize point-based synthetic customer data on an interactive Folium map.

    Parameters:
        shp_path (str): Path to the input shapefile or GeoPackage containing point data.
        sample_rate (float): Fraction of points to display (e.g., 0.05 = 5% sample).
        map_location (list): Initial center of the map [latitude, longitude]. Auto-calculated if None.
        zoom_start (int): Initial zoom level of the map.
        save_path (str or Path): Path to save the output HTML map.
    """
    # Load spatial data
    gdf = gpd.read_file(shp_path)
    gdf = gdf.to_crs(epsg=4326)  # Convert to WGS84 (lat/lon)

    # Keep only Point geometries
    gdf = gdf[gdf.geometry.type == 'Point']

    # Random sampling to reduce clutter
    sample_size = int(len(gdf) * sample_rate)
    sampled_gdf = gdf.sample(n=sample_size, random_state=42)

    # Auto-calculate map center if not provided
    if map_location is None:
        center = sampled_gdf.geometry.union_all().centroid
        map_location = [center.y, center.x]

    # Create Folium map
    fmap = folium.Map(location=map_location, zoom_start=zoom_start)

    # Define color palette and map
    colors = sns.color_palette("tab10", 7)
    hex_colors = [mcolors.rgb2hex(c) for c in colors]
    cate_color_map = {i: hex_colors[i] for i in range(7)}

    # Define category labels for legend
    cate_labels = {i: map_product(i) for i in range(7)}

    # separate lat, lon
    sampled_gdf['lat'] = sampled_gdf.geometry.y
    sampled_gdf['lon'] = sampled_gdf.geometry.x

    # group by (lat, lon)
    grouped = sampled_gdf.groupby(['lat', 'lon']).apply(
        lambda df: pd.Series({
            'popup_html': '<div style="font-size:12px; line-height:1.5; font-family:Arial;">' +
                        ''.join([f"<b>Customer ID:</b> {row['Customer_ID']}<br>"
                                f"<b>Order ID:</b> {row['Order_ID']}<br>"
                                f"<b>Area Code:</b> {row['area_code']}<br>"
                                f"<b>Category:</b> {row['cate_sample']}<br>"
                                f"---------------------<br>"
                                for _, row in df.iterrows()]) +
                        '</div>',
            'cate_sample': df.iloc[0]['cate_sample']  
        })
    ).reset_index()

    # Add coloured points to the map
    for _, row in grouped.iterrows():
        lat = row['lat']
        lon = row['lon']
        popup = folium.Popup(row['popup_html'], max_width=300)
        color = cate_color_map.get(row['cate_sample'], 'black')

        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color=color,
            fill=True,
            fill_opacity=0.9,
            popup=popup
        ).add_to(fmap)

    # Add legend
    legend_html = '''
    <div style="
        position:   fixed; 
        bottom:     25px;
        left:       30px; 
        width:      200px;
        height:     350px;
        border:     2px solid grey; 
        z-index:    9999; 
        font-size:  14px; 
        background-color:   white; 
        padding:    10px;
        overflow-y: auto; 
        ">
    <b style="font-size:18px;">Category Legend</b><br>
    '''

    for cat, color in cate_color_map.items():
        label = cate_labels.get(cat, f"Category {cat}")
        legend_html += f'<span style="color:{color}; font-size:20px;">&#9679;</span> {cat}: {label}<br>'

    # legend_html += '</div>'
    legend_html += f'''
    <p style="font-size:12px; color:gray; margin-top:10px;">
        Sample rate: {sample_rate*100:.1f}%
    </p>
    </div>
    '''

    fmap.get_root().html.add_child(folium.Element(legend_html))

    # Save the interactive map
    if save_path is None:
        save_path = "synthetic_orders_map.html"
    fmap.save(save_path)
    print(f"Map saved to: {save_path}")

show_syn_orders_map(
    shp_path=RES_path/ 'synthetic-order'/'synthetic_orders.gpkg',
    sample_rate=0.1,
    zoom_start=13,
    save_path=RES_path / 'html_maps' / 'synthetic_orders_map_10e5.html'
)
