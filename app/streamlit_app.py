import streamlit as st
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px

def change_page(page_name):
    st.session_state.current_page = page_name

def main():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

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
    st.write('Find your perfect county based on your preferences.')
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.button('Find Your Match', on_click=change_page, args=('preferences',), use_container_width=True)

def show_preferences_page():
    st.title('Set Your Preferences')
    
    # name
    user_name = st.text_input('What is your name?')
    
    st.markdown(
    """
    <style>
    .stSlider [role=slider] {
        background-color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True )

    # average age (red)
    age_list = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    age_preference = st.select_slider(
        'What is your perferred average age of the population?',
        options = age_list,
        value = 50,
        format_func=lambda x: str(x) 
    )

    # education (orange)
    education_preference = st.select_slider(
        'On a scale of 1 to 10, how important is high average education level to you? (1 = not important, 10 = very important)',
        options = list(range(1, 11)),
        value = 5,
        format_func=lambda x: str(x)
    )

    # prefered demographics (yellow)
    st.write("Which demographic groups are important to you? (Select all that apply)")
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

    # house ownership (green)
    houseownership_preference = st.select_slider(
        'How much do you value housing stability and ownership? (1 = prefer rental, 10 = prefer homeownership)',
        options = list(range(1, 11)),
        value = 5,
        format_func=lambda x: str(x)
    )

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
    
    # urban vs rural (dark red)
    population_preference = st.select_slider(
        'On a scale of 1 to 10, how much do you prefer urban vs rural areas? (1 = very rural, 10 = major metropolitan)',
        options = list(range(1, 11)),
        value = 5,
        format_func=lambda x: str(x)
    )

    # prefered storeowner demographic (blue)
    st.write("Which storeowner demographics are of high priority? (Select all that apply)")
    col1, col2, = st.columns(2)

    with col1:
        storeowner = {
            'woman owner': st.checkbox('Woman Owned'),
            'men owner': st.checkbox('Men Owned'),
            'minority owner': st.checkbox('Minority Owned'),
            'veteran owner': st.checkbox('Veteran Owned'),
        }

    storeowner_preferences = [key for key, value in storeowner.items() if value]
    
    # for degubbing, see text at bottom of screen
    if user_name:
        st.write(f'Hello, {user_name}!')
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
    st.write(f'You prefer a {population_map[population_preference]} area.')
    if demographic_preference:
        st.write(f"Selected demographics: {', '.join(demographic_preference)}")
    st.write(f'You prefer an average income of around ${income_value}k.')
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
    if storeowner_preferences:
        st.write(f"Selected demographics: {', '.join(storeowner_preferences)}")
    
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
        'Match Index': 'Age.Percent 65 and Older', # PLACEHOLDER
        'Elderly Population': 'Age.Percent 65 and Older',
        'Youth Population': 'Age.Percent Under 18 Years',
        'Education Level': "Education.Bachelor's Degree or Higher",
        'Income Level': 'Income.Median Houseold Income',
        'Housing Ownership': 'Housing.Homeownership Rate',
        'Population Density': 'Population.Population per Square Mile',
    }
    
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    # fips codes
    df = pd.read_csv('app/data/county_demographics.csv', dtype={"fips": str})

    df['fips'] = df['fips'].astype(str).str.zfill(5)

    display_column = metric_mapping[selected_metric]
    
    fig = px.choropleth(df, 
                       geojson=counties, 
                       locations='fips', 
                       color=display_column,
                       color_continuous_scale="PiYG",
                       range_color=(0, df[display_column].quantile(0.95)),  # Adjust range based on data
                       scope="usa",
                       labels={display_column: selected_metric},
                       hover_name='County',
                       hover_data={'fips': False, display_column: ':.1f'}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns([2, 6])
    with col1:
        st.button('Back to Results', on_click=change_page, args=('results',), use_container_width=True)

def show_results_page():
    st.title('Your County Match Results')
    st.write('Here are your top county matches based on your preferences.')
    # Placeholder for results content
    st.write('Results will be displayed here.')
    
    col1, col2, col3 = st.columns([1, 5, 2])
    with col1:
        st.button('Back', on_click=change_page, args=('preferences',), use_container_width=True)
    with col3:
        st.button('View Map', on_click=change_page, args=('map',), use_container_width=True)

if __name__ == '__main__':
    main()