#!/usr/bin/env python
# coding: utf-8

# In[68]:

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
from matplotlib.backends.backend_pdf import PdfPages 
from shapely import wkt
import argparse

parser = argparse.ArgumentParser(
    description= 'A program that makes an Atlas'
)
parser.add_argument('statefp', help='The STATEFP code: for example the STATEFP for North Carolina is 37')

# In[ ]:


statefp = '36'
url_0 = "https://www2.census.gov/geo/tiger/GENZ2024/shp/" 
url_county = "cb_2024_us_county_500k.zip"
url_state = "cb_2024_us_state_500k.zip"


# In[ ]:


counties = gpd.read_file(url_0 + url_county)
ny_counties = counties.loc[counties['STATEFP']== statefp].to_crs(4326)
#ny_counties.plot(edgecolor='black', facecolor='pink')


# In[71]:


parks = gpd.read_file("homework/week10/State_Park_Facility_Points_20261028.csv")
#parks


# In[72]:


#ny_counties


# In[73]:


parks['Georeference'] = parks['Georeference'].apply(wkt.loads)


# In[74]:


park_pts = gpd.GeoDataFrame(parks, geometry=parks['Georeference']).set_crs(4326, allow_override=True)


# In[75]:


parks_fixed = gpd.GeoDataFrame(
    park_pts.drop(columns="geometry", errors="ignore"),
    geometry=gpd.points_from_xy(
        park_pts["Longitude"],
        park_pts["Latitude"]
    ),
    crs="EPSG:4326"
)

parks_fixed = parks_fixed.to_crs(ny_counties.crs)

print(parks_fixed.total_bounds)
print(parks_fixed.geometry.head())


# In[76]:


#parks_fixed.plot()
#ny_counties.plot()


# In[77]:


ny_parks = gpd.sjoin(parks_fixed, ny_counties, 'inner', 'within')


# In[78]:


#ny_parks


# In[79]:


counts = ny_parks['NAME'].value_counts('index_right')
#counts


# In[80]:


num_counts = counts * 253
#num_counts


# In[81]:


num_counts.to_dict()


# In[82]:


num_counts // 1


# In[83]:


num_counts.sum()


# In[ ]:


def county_map(county, ax):
    selected = ny_counties[ny_counties["NAME"] == county]
    selected.plot(ax=ax, edgecolor="black", facecolor="#7b9b90")
    ax.set_axis_off()
def locator_map(county, ax):
    selected = ny_counties[ny_counties["NAME"] == county]
    ny_counties.plot(ax=ax, edgecolor="gray", facecolor="white")
    selected.plot(ax=ax, edgecolor="black", facecolor="#7b9b90")
    ax.set_axis_off()
def county_figure(county, pdf):
    fig, axes = plt.subplots(
        2, 1,
        figsize=(8, 10),
        gridspec_kw={"height_ratios": [3, 1]}
    )

    county_map(county, axes[0])
    locator_map(county, axes[1])

    fig.suptitle(f"{county} County", fontsize=20)

    pdf.savefig(fig)
    plt.close(fig)
def county_pie(county, ax):
    selected = ny_counties[ny_counties["NAME"] == county]

    land = selected["ALAND"].iloc[0]
    water = selected["AWATER"].iloc[0]

    ax.pie(
        [land, water],
        labels=["Land", "Water"],
        colors=["olivedrab", "steelblue"],
        autopct="%.1f%%",
        startangle=90
    )

    ax.set_title("Land and water")
def county_info(county, ax):
    selected = ny_counties[ny_counties["NAME"] == county]

    land = selected["ALAND"].iloc[0]
    water = selected["AWATER"].iloc[0]
    park_val = num_counts.get(county, 0)

    ## Using ai and https://matplotlib.org/stable/gallery/shapes_and_collections/hatch_demo.html
    # Land icon: mountains
    mountain = Polygon(
        [(0.02, 0.60), (0.09, 0.80), (0.14, 0.69),
         (0.19, 0.76), (0.25, 0.60)],
        facecolor="olivedrab",
        transform=ax.transAxes
    )
    ax.add_patch(mountain)

    # Water icon
    lake = Ellipse(
        (0.13, 0.30),
        width=0.23,
        height=0.12,
        facecolor="steelblue",
        transform=ax.transAxes
    )
    ax.add_patch(lake)

    ax.text(
        0.32, 0.80,
        f"LAND\n{land / 1_000_000:,.2f} km²\n"
        f"{land / 2_589_988.110336:,.2f} square miles",
        transform=ax.transAxes,
        fontsize=14,
        color="olivedrab",
        va="top"
    )

    ax.text(
        0.32, 0.40,
        f"WATER\n{water / 1_000_000:,.2f} km²\n"
        f"{water / 2_589_988.110336:,.2f} square miles",
        transform=ax.transAxes,
        fontsize=14,
        color="steelblue",
        va="top"
    )

    if park_val != 1:
        ax.text(
            0.05, 0.90,
            f"{park_val} parks",
            fontsize= 14,
            color = '#0a481e',
            va= 'top'
        )
    else:
        ax.text(
            0.05, 0.90,
            f"{park_val} park",
            fontsize= 14,
            color = '#0a481e',
            va= 'top'
        )

    ax.set_axis_off()
def county_figure(county, pdf):

    fig = plt.figure(figsize=(12, 8))

    # [left, bottom, width, height] as fractions of the figure
    # Coded with Ai help
    ax_county = fig.add_axes([0.05, 0.23, 0.55, 0.54])
    ax_locator = fig.add_axes([0.05, 0.08, 0.25, 0.12])
    ax_pie = fig.add_axes([0.65, 0.48, 0.30, 0.30])
    ax_info = fig.add_axes([0.65, 0.12, 0.30, 0.32])


    county_map(county, ax_county)
    locator_map(county, ax_locator)
    county_pie(county, ax_pie)
    county_info(county, ax_info)

    # Page heading
    fig.text(
        0.05, 0.94,
        f"State FP: {statefp} / County Water-Land Atlas",
        fontsize=10,
        color="olivedrab"
    )

    fig.text(
        0.05, 0.87,
        f"{county} County",
        fontsize=28,
        fontweight="bold"
    )

    # Footer
    fig.text(
        0.05, 0.03,
        "Source: U.S. Census Bureau | Areas from ALAND and AWATER",
        fontsize=9,
        color="gray"
    )

    pdf.savefig(fig, dpi=50)
    plt.close(fig)


# In[86]:


fig, axes = plt.subplots(
    1, 2,
    figsize=(12, 6),
)
county_map("Bronx", axes[0])
locator_map("Bronx", axes[1])


# In[ ]:


ny_sorted = ny_counties.sort_values('NAME').reset_index(drop=True)

with PdfPages('NY_Counties.pdf') as pdf:
    for county in ny_sorted['NAME']:
        county_figure(county, pdf)

