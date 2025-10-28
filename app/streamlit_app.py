import streamlit as st

def main():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    # change displays 
    if st.session_state.current_page == 'home':
        show_home_page()
    elif st.session_state.current_page == 'preferences':
        show_preferences_page()

def show_home_page():
    st.title('Welcome to County Matchmaker!')
    st.write('Find your perfect county based on your preferences.')
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('Find your match', use_container_width=True):
            st.session_state.current_page = 'preferences'

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
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button('back', use_container_width=True):
            st.session_state.current_page = 'home'

if __name__ == '__main__':
    main()