import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(layout="wide",page_title='StartUp Analysis')
df=pd.read_csv('cleaned_data.csv')

df['date'] = pd.to_datetime(df['date'], errors='coerce')

def load_investor_details(investor):
    st.title(investor)
    investor_df = df[df['investors'].str.contains(investor)]

    last5_df = investor_df.sort_values('date', ascending=False).head(5)

    last5_df = last5_df[['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.dataframe(last5_df)


    col1 , col2 , col3 , col4 = st.columns(4)
    with col1:
        big_series = df[df['investors'].str.contains(investor)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        st.subheader('Biggest Invetments')
        st.dataframe(big_series)
        fig,ax= plt.subplots()
        ax.bar(big_series.index ,big_series.values )
        st.pyplot(fig)

    with col2:
        vertical_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount'].sum()
        st.subheader('Sectors invested')
        st.dataframe(vertical_series)
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series , labels = vertical_series.index  , autopct='%1.1f%%')
        st.pyplot(fig1)


    with col3:
        round_series = df[df['investors'].str.contains(investor)].groupby('round')['amount'].sum()
        st.subheader('ROUND Invetments')
        st.dataframe(round_series)
        fig2,ax2= plt.subplots()
        ax2.pie(round_series , labels = round_series.index , autopct = '%1.1f%%')
        st.pyplot(fig2)

    with col4:
        city_series = df[df['investors'].str.contains(investor)].groupby('city')['amount'].sum()
        st.subheader('CITY Invetments')
        st.dataframe(city_series)
        fig3,ax3= plt.subplots()
        ax3.pie(city_series, labels = city_series.index , autopct = '%1.1f%%')
        st.pyplot(fig3)


    #Year on Year invetment chart
    df['year'] = df['date'].dt.year
    year_series = df[df['investors'].str.contains(investor)].groupby('year')['amount'].sum().sort_index()
    st.subheader('YEAR Invetments')
    st.dataframe(year_series)
    fig4,ax4= plt.subplots()
    ax4.plot(year_series.index , year_series.values)
    st.pyplot(fig4)


def load_overall_analysis():
    st.title('Overall Analysis')

    total_funded = round(df['amount'].sum())
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).iloc[0]
    avg_funding = round(df['amount'].mean())
    num_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Total Funding', f'{total_funded} Cr')
    with col2:
        st.metric('Max Funding', f'{max_funding} Cr')
    with col3:
        st.metric('Average Funding', f'{avg_funding} Cr')
    with col4:
        st.metric('Total Funded Startups', num_startups)

    st.header('Month-on-Month Investment Graph')
    selected_option = st.selectbox('Select Type', ['Total Amount', 'Count of Investments'])

    df['month_year'] = df['date'].dt.to_period('M')

    if selected_option == 'Total Amount':
        mom_series = df.groupby('month_year')['amount'].sum().reset_index()
        mom_series['month_year'] = mom_series[
            'month_year'].dt.to_timestamp()  # Convert period to timestamp for plotting
        st.line_chart(mom_series.set_index('month_year')['amount'])
    else:
        mom_count_series = df.groupby('month_year')['startup'].count().reset_index()
        mom_count_series['month_year'] = mom_count_series['month_year'].dt.to_timestamp()
        st.line_chart(mom_count_series.set_index('month_year')['startup'])

    col5, col6 = st.columns(2)
    with col5:
        top_sectors = df.groupby('vertical')['amount'].sum().nlargest(5)
        st.subheader('Top 5 Funded Sectors')
        st.bar_chart(top_sectors)

    with col6:
        df['investors_split'] = df['investors'].str.split(', ')
        top_investors = df.explode('investors_split').groupby('investors_split')['amount'].sum().nlargest(5)
        st.subheader('Top 5 Investors (by Amount)')
        st.bar_chart(top_investors)


def load_startup_details(startup):
    st.title(startup)

    startup_df = df[df['startup'] == startup]

    vertical = startup_df['vertical'].iloc[0]
    city = startup_df['city'].iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        st.metric('Industry/Vertical', vertical)
    with col2:
        st.metric('Location/City', city)

    st.subheader('Funding Rounds')
    st.dataframe(startup_df[['date', 'round', 'investors', 'amount']])


st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('Select one', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp':
    selected_startup = st.sidebar.selectbox('Select Startup', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Find Startup Details')
    if btn1:
        load_startup_details(selected_startup)

else:  # This is the Investor option
    investor_list = df['investors'].str.split(', ')
    unique_investors = sorted(list(
        set([investor.strip() for sublist in investor_list.dropna() for investor in sublist if
             investor.strip() != 'Undisclosed Investors'])))

    selected_investor = st.sidebar.selectbox('Select Investor', unique_investors)
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)