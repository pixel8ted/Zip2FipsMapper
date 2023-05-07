import geopandas as gpd
import json

# Download latest census shapefile (ZIP Code Tabulation Areas)
# https://www.census.gov/cgi-bin/geo/shapefiles/index.php?layergroup=ZIP+Code+Tabulation+Areas
shapefile_path = "./resources/tl_2022_us_zcta520/tl_2022_us_zcta520.shp"
# Download latest census shapefile (Counties (and equivalent))
# https://www.census.gov/cgi-bin/geo/shapefiles/index.php?layergroup=Counties+%28and+equivalent%29
county_shapefile_path = "./resources/tl_2022_us_county/tl_2022_us_county.shp"

def generate_fips_mapping():
    state_fips_to_abbreviation = {}
    with open('./resources/state.txt', 'r') as f:
        for line in f.readlines():
            fields = line.strip().split('|')
            state_fips_to_abbreviation[fields[0]] = fields[1]

    # Load shapefiles
    zcta_shapefile = gpd.read_file(shapefile_path)

    # Load county shapefile
    county_shapefile = gpd.read_file(county_shapefile_path)
    county_shapefile['state_abbreviation'] = county_shapefile['STATEFP'].apply(
        lambda x: state_fips_to_abbreviation.get(x, ''))

    print(zcta_shapefile.columns)
    print(county_shapefile.columns)

    # Perform spatial join
    joined_shapefile = gpd.sjoin(zcta_shapefile, county_shapefile[['GEOID', 'NAME', 'state_abbreviation', 'geometry']],
                                 op='intersects', how='left')

    # Extract ZIP codes and corresponding FIPS codes
    zip_fips_data = joined_shapefile[['ZCTA5CE20', 'GEOID', 'NAME', 'state_abbreviation']]
    zip_fips_data.columns = ['zip', 'fips', 'county_name', 'state_abbreviation']

    zip_fips_data.to_csv('zip_fips_data.csv', index=False)

    zip_fips_mapping = {}
    for index, row in zip_fips_data.iterrows():
        zip_fips_mapping[row['zip']] = {
            'fips': row['fips'],
            'county_name': row['county_name'],
            'state_abbreviation': row['state_abbreviation']
        }

    with open('zip_fips_mapping.json', 'w') as outfile:
        json.dump(zip_fips_mapping, outfile)

if __name__ == '__main__':
    generate_fips_mapping()

