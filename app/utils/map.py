from urllib.request import urlopen
import json
import pandas as pd
from urllib.request import urlopen

# so it know what fips code is for each county
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# fips codes
df = pd.read_csv('app/data/county_demographics.csv', dtype={"fips": str})

df['fips'] = df['fips'].astype(str).str.zfill(5)

fig = px.choropleth(df, geojson=counties, locations='fips', color='Age.Percent 65 and Older',
                           color_continuous_scale="PiYG",
                           range_color=(0, 50),
                           scope="usa",
                           labels={'Age.Percent 65 and Older':'Percent 65 and Older'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()