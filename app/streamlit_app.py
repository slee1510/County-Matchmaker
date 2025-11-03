import streamlit as st
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px
from algorithms.dijkstra import dijkstra_algorithm
from algorithms.bellman_ford import bellman_ford_algorithm
import os

if "features" not in st.session_state:
    st.session_state.features = {}

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def change_page(page_name):
    st.session_state.current_page = page_name

def main():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    css_path = os.path.join('app', 'static', 'css', 'style.css')
    local_css(css_path)

    # change displays 
    if st.session_state.current_page == 'home':
        show_home_page()
    elif st.session_state.current_page == 'preferences':
        show_preferences_page()
    elif st.session_state.current_page == 'map':
        show_map_page()
    elif st.session_state.current_page == 'results':
        show_results_page()

def show_home_page():
    st.title('Welcome to County Matchmaker!')
    st.markdown('<p class="homepage-subtitle">Find your perfect county based on your preferences.</p>', unsafe_allow_html=True)    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.button('Find Your Match', on_click=change_page, args=('preferences',), use_container_width=True)

def show_preferences_page():
    preferences = {}
    features = st.session_state.features

    st.title('Set Your Preferences')
    
    # name
    user_name = st.text_input('What is your name?')
    
    # average age (red)
    age_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    age_preference = st.select_slider(
        'What is your perferred average age of the population?',
        options = age_list,
        value = 50,
        format_func=lambda x: str(x) 
    )

    if age_preference >= 60:
        features["Age.Percent 65 and Older"] = 0.6
        features["Age.Percent Under 18 Years"] = 0.3
        features["Age.Percent Under 5 Years"] = 0.1
    else:
        features["Age.Percent 65 and Older"] = 0.3
        features["Age.Percent Under 18 Years"] = 0.6
        features["Age.Percent Under 5 Years"] = 0.1

    # education (orange)
    education_preference = st.select_slider(
        'On a scale of 1 to 10, how important is high average education level to you? (1 = not important, 10 = very important)',
        options = list(range(1, 11)),
        value = 5,
        format_func=lambda x: str(x)
    )

    features["Education.Bachelor's Degree or Higher"] = education_preference / 10.0
    features["Education.High School or Higher"] = 1 - (education_preference / 10.0)

    # prefered demographics (yellow)
    st.subheader("Which demographic groups are important to you? (Select all that apply)")
    col1, col2 = st.columns(2)
    
    with col1:
        demographics = {
            'native': st.checkbox('American Indian/Alaska Native'),
            'asian': st.checkbox('Asian'),
            'black': st.checkbox('Black or African American'),
            'hispanic': st.checkbox('Hispanic or Latino'),
            'pacific': st.checkbox('Pacific Islander'),
            'white': st.checkbox('White'),
            'female': st.checkbox('Female'),
            'veteran': st.checkbox('Veteran'),
        }

    demographic_preference = [key for key, value in demographics.items() if value]

    if len(demographic_preference) != 0:
        demographic_percentage = 1.0 / len(demographic_preference)

    features["Miscellaneous.Foreign Born"] = 0.0
    features["Miscellaneous.Language Other than English at Home"] = 0.0
    features["Ethnicities.American Indian and Alaska Native Alone"] = 0.0
    features["Ethnicities.Asian Alone"] = 0.0
    features["Ethnicities.Black Alone"] = 0.0
    features['Ethnicities.Hispanic or Latino'] = 0.0
    features['Ethnicities.Native Hawaiian and Other Pacific Islander Alone'] = 0.0
    features['Ethnicities.White Alone'] = 0.0
    features['Miscellaneous.Percent Female'] = 0.0
    features['Miscellaneous.Veterans'] = 0.0
    features['Ethnicities.Two or More Races'] = 0.0
    features['Ethnicities.White Alone	 not Hispanic or Latino'] = 0.0

    if 'native' in demographic_preference:
        features["Ethnicities.American Indian and Alaska Native Alone"] = demographic_percentage
    if 'asian' in demographic_preference:
        features["Ethnicities.Asian Alone"] = demographic_percentage
        features["Miscellaneous.Foreign Born"] = 0.3
        features["Miscellaneous.Language Other than English at Home"] = 0.3
    if 'black' in demographic_preference:
        features["Ethnicities.Black Alone"] = demographic_percentage
        features["Miscellaneous.Foreign Born"] = 0.3  
    if 'hispanic' in demographic_preference:
        features["Ethnicities.Hispanic or Latino"] = demographic_percentage
        features["Miscellaneous.Foreign Born"] = 0.3
        features["Miscellaneous.Language Other than English at Home"] = 0.3
    if 'pacific' in demographic_preference:
        features["Ethnicities.Native Hawaiian and Other Pacific Islander Alone"] = demographic_percentage
        features["Miscellaneous.Foreign Born"] = 0.3
        features["Miscellaneous.Language Other than English at Home"] = 0.3
    if 'white' in demographic_preference:
        features["Ethnicities.White Alone"] = demographic_percentage
    if 'female' in demographic_preference:
        features["Miscellaneous.Percent Female"] = demographic_percentage
    if 'veteran' in demographic_preference:
        features["Miscellaneous.Veterans"] = demographic_percentage
    if len(demographic_preference) > 1: 
        features['Ethnicities.Two or More Races'] = 1.0
    if 'white' in demographic_preference and "hispanic" not in demographic_preference:
        features['Ethnicities.White Alone	 not Hispanic or Latino'] = 1.0

    # house ownership (green)
    houseownership_preference = st.select_slider(
        'How much do you value housing stability and ownership? (1 = prefer rental, 10 = prefer homeownership)',
        options = list(range(1, 11)),
        value = 5,
        format_func=lambda x: str(x)
    )

    if houseownership_preference >= 6:
        features["Housing.Homeownership Rate"] = 1.0
        features["Housing.Households"] = 1.0
        features["Housing.Housing Units"] = 1.0
        features["Miscellaneous.Living in Same House +1 Years"] = 1.0
    else:
        features["Housing.Homeownership Rate"] = 0.0
        features["Housing.Households"] = 1.0
        features["Housing.Housing Units"] = 1.0
        features["Miscellaneous.Living in Same House +1 Years"] = 0.0

    # average income (purple])
    myListIncome = ["25", "50", "75", "100", "125", "150", "175", "200", "225", "250", "275", "300+"]
    income_preference = st.select_slider(
        'Prefered average income? (in thousands)',
        options = myListIncome,
        value = "175",
    )
    if income_preference == "300+":
        income_value = 400; 
    else:
        income_value = int(income_preference)

    income_percentage = income_value / 300
    features["Housing.Median Value of Owner-Occupied Units"] = income_percentage
    features["Income.Median Household Income"] = income_percentage
    features["Income.Per Capita Income"] = income_percentage
                 
    # urban vs rural (dark red)
    population_preference = st.select_slider(
        'On a scale of 1 to 10, how much do you prefer urban vs rural areas? (1 = very rural, 10 = major metropolitan)',
        options = list(range(1, 11)),
        value = 5,
        format_func=lambda x: str(x)
    )

    features['Population.Population per Square Mile'] = population_preference / 10
    features['Sales.Accommodation and Food Services Sales'] = population_preference / 10
    features['Sales.Retail Sales'] = population_preference / 10
    features['Miscellaneous.Manufacturers Shipments'] = population_preference / 10
    features['Miscellaneous.Mean Travel Time to Work'] = population_preference / 10
    features['Employment.Firms.Total'] = population_preference / 10

    # prefered storeowner demographic (blue)
    st.subheader("Which storeowner demographics are of high priority? (Select all that apply)")
    col1, col2, = st.columns(2)

    with col1:
        storeowner = {
            'woman owner': st.checkbox('Woman Owned'),
            'men owner': st.checkbox('Men Owned'),
            'minority owner': st.checkbox('Minority Owned'),
            'veteran owner': st.checkbox('Veteran Owned'),
        }

    storeowner_preferences = [key for key, value in storeowner.items() if value]

    features['Employment.Firms.Women-Owned'] = 0.0
    features['Employment.Firms.Men-Owned'] = 0.0
    features['Employment.Firms.Minority-Owned'] = 0.0
    features['Employment.Firms.Nonminority-Owned'] = 1.0
    features['Employment.Firms.Veteran-Owned'] = 0.0
    features['Employment.Firms.Nonveteran-Owned'] = 1.0

    if 'women owner' in storeowner:
        features['Employment.Firms.Women-Owned'] = 1.0
    if 'men owner' in storeowner:
        features['Employment.Firms.Men-Owned'] = 1.0
    if 'minority owner' in storeowner:
        features['Employment.Firms.Minority-Owned'] = 1.0
        features['Employment.Firms.Nonminority-Owned'] = 0.0
    if 'veteran owner' in storeowner:
       features['Employment.Firms.Veteran-Owned'] = 1.0
       features['Employment.Firms.Nonveteran-Owned'] = 0.0

    # for degubbing, see text at bottom of screen
    if user_name:
        st.subheader(f'Hello, {user_name}!')
    st.subheader("Summary:")
    st.write(f'You prefer an average population age of around {age_preference}.')
    education_map = {
        1: "very low",
        2: "very low",
        3: "low ",
        4: "low",
        5: "medium",
        6: "medium",
        7: "high",
        8: "high",
        9: "very high",
        10: "very high"
    }
    preferences['age'] = age_preference
    st.write(f'You have a {education_map[education_preference]} preference for high level of education.')
    population_map = {
        1: "very rural",
        2: "rural",
        3: "somewhat rural",
        4: "small town",
        5: "medium town",
        6: "large town",
        7: "small city",
        8: "medium city",
        9: "large city",
        10: "major metropolitan"
    }
    preferences['education'] = education_preference
    st.write(f'You prefer a {population_map[population_preference]} area.')
    preferences['population'] = population_preference
    if demographic_preference:
        st.write(f"Selected demographics: {', '.join(demographic_preference)}")
        preferences['demographics'] = demographic_preference
    st.write(f'You prefer an average income of around ${income_preference}k.')
    preferences['income'] = income_value
    house_map = {
        1: "prefer rental",
        2: "prefer rental",
        3: "slightly prefer rental",
        4: "slightly prefer rental",
        5: "are neutral about renting vs ownership",
        6: "are neutral about renting vs ownership",
        7: "slightly prefer homeownership",
        8: "slightly prefer homeownership",
        9: "prefer homeownership",
        10: "prefer homeownership"
    }
    st.write(f'You {house_map[houseownership_preference]}.')
    preferences['houseownership'] = houseownership_preference
    if storeowner_preferences:
        st.write(f"Selected demographics: {', '.join(storeowner_preferences)}")
        preferences['storeowner'] = storeowner_preferences
    
    # back button
    col1, col2, col3 = st.columns([1, 5, 2])
    with col1:
        st.button('Back', on_click=change_page, args=('home',), use_container_width=True)
    with col3:
        st.button('See Your Results', on_click=change_page, args=('results',), use_container_width=True)

def show_map_page():
    st.title('Map Display')
    st.write('Hover to see county details.')

    # Add metric selector dropdown
    selected_metric = st.selectbox(
        'Select data to display:',
        options=[
            'Match Index',
            'Elderly Population',
            'Youth Population',
            'Education Level',
            'Income Level',
            'Housing Ownership',
            'Population Density',
        ],
        index=0
    )
    metric_mapping = {
        'Match Index': 'DistanceToIdeal',
        'Elderly Population': 'Age.Percent 65 and Older',
        'Youth Population': 'Age.Percent Under 18 Years',
        'Education Level': "Education.Bachelor's Degree or Higher",
        'Income Level': 'Income.Median Household Income',
        'Housing Ownership': 'Housing.Homeownership Rate',
        'Population Density': 'Population.Population per Square Mile',
    }

    if selected_metric == 'Match Index':
        st.write('Counties with lower Match Index values are better matches to your preferences.')
    elif selected_metric == 'Elderly Population':
        st.write('Scale is percentage of population aged 65 and older.')
    elif selected_metric == 'Youth Population':
        st.write('Scale is percentage of population under 18 years old.')
    elif selected_metric == 'Education Level':
        st.write("Scale is percentage of population with a Bachelor's degree or higher.")
    elif selected_metric == 'Income Level':
        st.write('Scale is median household income normalized to $300,000.')
    elif selected_metric == 'Housing Ownership':
        st.write('Scale is homeownership rate in percentage.')
    elif selected_metric == 'Population Density':
        st.write('Scale is population per square mile normalized.')

    try:
        # Load GeoJSON for US counties
        with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
            counties = json.load(response)

        # Load and prepare county data
        csv_path = 'app/data/county_demographics_with_distances.csv'
        df = pd.read_csv(csv_path, dtype={"fips": str})
        # Clean up FIPS codes - remove decimals and ensure 5-digit format
        df['fips'] = df['fips'].astype(str).apply(lambda x: x.split('.')[0].zfill(5))

        display_column = metric_mapping[selected_metric]

        # Quantile-based normalization: spreads colors evenly across values
        valid_count = df[display_column].notna().sum()
        if valid_count > 0:
            df['__norm'] = (df[display_column].rank(method='average', na_option='keep') - 0.5) / float(valid_count)
        else:
            df['__norm'] = pd.NA

        # Color scale: for Match Index lower is better -> green
        color_scale = "RdYlGn_r" if selected_metric == 'Match Index' else "RdYlGn"

        fig = px.choropleth(
            df,
            geojson=counties,
            locations='fips',
            color='__norm',
            color_continuous_scale=color_scale,
            range_color=(0, 1),
            scope="usa",
            labels={'__norm': selected_metric},
            hover_name='County',
            hover_data={'fips': False, display_column: ':.3f'}
        )

        # Show colorbar ticks in original units for readability
        q_levels = [0.05, 0.25, 0.5, 0.75, 0.95]
        quantiles = df[display_column].quantile(q_levels)
        def _fmt(v):
            try:
                v = float(v)
            except Exception:
                return str(v)
            if abs(v) >= 1000:
                return f"{v:,.0f}"
            if abs(v) >= 100:
                return f"{v:.0f}"
            if abs(v) >= 10:
                return f"{v:.1f}"
            return f"{v:.2f}"
        tickvals = q_levels
        ticktext = [_fmt(quantiles.get(q)) for q in q_levels]
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            coloraxis_colorbar=dict(
                title=selected_metric,
                tickvals=tickvals,
                ticktext=ticktext
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error displaying map: {str(e)}")

    col1, col2 = st.columns([2, 6])
    with col1:
        st.button('Start Over', on_click=change_page, args=('home',), use_container_width=True)

def show_results_page():
    features = st.session_state.features
    st.title('Your County Match Results')
    st.markdown('<p class="homepage-subtitle">Choose an algorithm.</p>', unsafe_allow_html=True)    
    runDijkstra = False
    runBellman = False

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button('Run Dijkstra', use_container_width=True):
            runDijkstra = True; 
            result, elapsed_time = dijkstra_algorithm(features)
    with col2:
        if st.button('Run Bellman-Ford', use_container_width=True):
            runBellman = True; 
            result, elapsed_time = bellman_ford_algorithm(features)

    if runDijkstra:
        st.success(f"Dijkstra's algorithm search for ideal county completed in {elapsed_time:.3f} seconds")
        st.markdown('<p class="homepage-subtitle">Your best match:</p>', unsafe_allow_html=True)    
        try:
            # Handle Series or DataFrame directly to avoid JSON string formatting
            row = result.iloc[0] if hasattr(result, 'iloc') else result
            county = None
            state = None
            if hasattr(row, 'get'):
                county = row.get('County') or row.get('county')
                state = row.get('State') or row.get('state')
            if county is None or state is None:
                # Fallback: try JSON parsing if needed
                record = json.loads(result.to_json()) if hasattr(result, 'to_json') else None
                if isinstance(record, dict):
                    county = county or record.get('County') or record.get('county')
                    state = state or record.get('State') or record.get('state')
            if county and state:
                st.markdown(f'<p class="result-text">{county}, {state}</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p class="result-text">{str(result)}</p>', unsafe_allow_html=True)
        except Exception:
            st.markdown(f'<p class="result-text">{str(result)}</p>', unsafe_allow_html=True)
        runDijkstra = True
    elif runBellman:
        st.success(f"Bellman-Ford's algorithm search for ideal county completed in {elapsed_time:.3f} seconds")
        st.markdown('<p class="homepage-subtitle">Your best match:</p>', unsafe_allow_html=True)    
        try:
            row = result.iloc[0] if hasattr(result, 'iloc') else result
            county = None
            state = None
            if hasattr(row, 'get'):
                county = row.get('County') or row.get('county')
                state = row.get('State') or row.get('state')
            if county is None or state is None:
                record = json.loads(result.to_json()) if hasattr(result, 'to_json') else None
                if isinstance(record, dict):
                    county = county or record.get('County') or record.get('county')
                    state = state or record.get('State') or record.get('state')
            if county and state:
                st.markdown(f'<p class="result-text">{county}, {state}</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p class="result-text">{str(result)}</p>', unsafe_allow_html=True)
        except Exception:
            st.markdown(f'<p class="result-text">{str(result)}</p>', unsafe_allow_html=True)
        runBellman = True
    
    if (runDijkstra or runBellman):
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
        with col1:
            st.button('Start Over', on_click=change_page, args=('home',), use_container_width=True)
        with col4:
            st.button('View Map', on_click=change_page, args=('map',), use_container_width=True)

if __name__ == '__main__':
    main()
