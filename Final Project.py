import streamlit as st
import pydeck as pdk
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image


#Add new column named "STATE" to the dataframe
def getting_state(departure): #Filter out other places like foreign countries to make sure there's only state in the "STATE" column
    not_state = ["GB", "UK", "NZ", "NS", "NF", "NB", "SA"]
    departure = str(departure)
    list = departure.split(",")
    for item in list:
        if item.strip().upper() in not_state:
            list.remove(item)
    if len(list[-1].strip()) == 2: #State in "DEPARTURE PORT" column is only two letters
        result = list[-1].strip()
    else:
        result = ""
    return result

#Descriptive statistics
def stats(datafile,state = "NJ"):
    newfile = datafile.loc[datafile["STATE"] == state]
    newfile = newfile.dropna(subset=["LIVES LOST"])
    newfile = newfile[pd.to_numeric(newfile["LIVES LOST"],errors = "coerce").notnull()]
    newfile["LIVES LOST"] = newfile["LIVES LOST"].astype(float)
    liveslost = newfile["LIVES LOST"]
    count = len(liveslost)
    mean = liveslost.mean()
    minimum = liveslost.min()
    maximum = liveslost.max()
    return count, mean, minimum, maximum

#Create a horizontal histogram whoing the top 5 vessels that has the most shipwrecks with the number of shipwrecks occurs
def vessle_type(state, datafile,option = "ascending"):
    vessel_dic = {}
    newfile = datafile.loc[datafile["STATE"] == state]
    newfile = newfile[newfile["VESSEL TYPE"].notnull()]

    for row in newfile.itertuples():
        if row[4] in vessel_dic:
            vessel_dic[row[4]] += 1
        else:
            vessel_dic[row[4]] = 1

    tuple_list = []
    for key, value in vessel_dic.items():
        tuple_list.append((value, key))
    tuple_list.sort(reverse=True)
    if len(tuple_list) >= 5:
        tuple_list = tuple_list[:5]
    else:
        tuple_list = tuple_list[:-1]

    x = [x[0] for x in tuple_list]
    y = [y[1] for y in tuple_list]
    colorlist = ['red', 'green', 'blue', 'yellow', 'black']
    if option == "ascending":
        x = x
        colorlist = colorlist
    elif option == "descending":
        x.sort()
        y = y[::-1]
        colorlist = colorlist[:len(y)]
        colorlist = colorlist[::-1]


    fig, ax = plt.subplots()
    barlist = ax.barh(y, x, label = y)
    ax.set_title("Top-5 Vessels that Contain Most Number of Shipwrecks")
    ax.set_xlabel("Shipwreck Frequency")
    ax.set_ylabel("Vessel Type")
    for i in range(len(barlist)):
        barlist[i].set_color(colorlist[i])
    plt.legend()

    st.pyplot(fig)

    with st.expander("See explanation"):
        st.write("The chart above shows the vessel types that contain the most number of shipwrecks. Notice that sometimes there will be vessel types fewer than 5 since some states doesn't have shipwrecks that many as other states.")

#create a scatterplot of the number of lives loss in each year
def scatter_plot(state, datafile):
    newfile = datafile.loc[datafile["STATE"] == state]
    newfile = newfile.dropna(subset=["LIVES LOST"])
    newfile = newfile.sort_values('LIVES LOST', ascending=True)
    newfile = newfile[pd.to_numeric(newfile["LIVES LOST"], errors="coerce").notnull()]
    newfile["LIVES LOST"] = newfile["LIVES LOST"].astype(float)
    year = newfile["YEAR"]
    lives = newfile["LIVES LOST"]

    fig, ax = plt.subplots()
    ax.scatter(year, lives, marker='*', color='r')
    ax.set_xlabel('Year')
    ax.set_ylabel('Lives lost')
    ax.set_title('Number of Lives lost in years')

    st.pyplot(fig)
    with st.expander("See explanation"):
        st.write("The chart above shows the scatterplot of the number of lives lost in different years. Notice that some states may have empty scatterplot since there's no casualties occurred.")

#create some Streamlit widgets that allows users to choose the type of vessels they like and display the corresponding picutre and download button
def interact():
    genre = st.radio(
        "What is your favorite vessel type?",
        ('Schooner', 'Barge', 'Steamship'))

    if genre == 'Schooner':
        st.write('You selected Schooner, pairing you with a Schooner image...')
        image = Image.open('nicole-chen-hvarYahLAxc-unsplash.jpg')
        st.image(image, caption='Schooner')
        with open("nicole-chen-hvarYahLAxc-unsplash.jpg", "rb") as file:
            btn = st.download_button(
                label="Download image",
                data=file,
                file_name="nicole-chen-hvarYahLAxc-unsplash.jpg",
                mime="image/jpg"
            )
    elif genre == 'Barge':
        st.write("You selected Barge, pairing you with a Barge image...")
        image = Image.open('guido-knook-vKX--EcHvoo-unsplash (1).jpg')
        st.image(image, caption='Barge')
        with open("guido-knook-vKX--EcHvoo-unsplash (1).jpg", "rb") as file:
            btn = st.download_button(
                label="Download image",
                data=file,
                file_name="guido-knook-vKX--EcHvoo-unsplash (1).jpg",
                mime="image/jpg"
            )
    else:
        st.write("You selected Steamship, pairing you with a Steamship image...")
        image = Image.open('michael-944sDSMQ778-unsplash.jpg')
        st.image(image, caption='Steamship')
        with open("michael-944sDSMQ778-unsplash.jpg", "rb") as file:
            btn = st.download_button(
                label="Download image",
                data=file,
                file_name="michael-944sDSMQ778-unsplash.jpg",
                mime="image/jpg"
            )

#create a map showing where the shipwrecks occured on a map
def map(datafile):
    datafile = datafile[["LONGITUDE_BACKUP","LATITUDE_BACKUP","SHIP'S NAME","VESSEL TYPE"]].replace("-", None)
    datafile = datafile.dropna()
    # I used lambda function for the below two lines
    datafile["lat"] = datafile["LONGITUDE_BACKUP"].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    datafile["lon"] = datafile["LATITUDE_BACKUP"].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    newfile = datafile.dropna(subset=["lat", "lon"])

    layer1 = pdk.Layer('ScatterplotLayer',
                       data=newfile,
                       get_position='[lon, lat]',
                       get_radius=10000,
                       get_color=[255, 255, 255],
                       pickable=True)
    tool_tip = {"html": "Ship's name:<br/> <b>{SHIP'S NAME}</b><br/>Vessel type:<br/> <b>{VESSEL TYPE}</b>",
                "style": {"backgroundColor": "steelblue",
                          "color": "white"}}

    view_state = pdk.ViewState(
        latitude=newfile["lat"].mean(),
        longitude=newfile["lon"].mean(),
        zoom=4,
        pitch=50
    )

    map = pdk.Deck(layers=[layer1], initial_view_state=view_state, tooltip= tool_tip)
    st.pydeck_chart(map)

#create a line graph showing the average ship value in dollar in different years
def line_graph(state, datafile):
    newfile = datafile.loc[datafile["STATE"] == state]
    newfile = newfile.dropna(subset=["YEAR"])
    newfile = newfile.dropna(subset=["SHIP VALUE"])
    newfile["SHIP VALUE"] = newfile["SHIP VALUE"].str.replace('$','',regex = False)
    newfile["SHIP VALUE"] = newfile["SHIP VALUE"].str.replace(',', '',regex = False)
    newfile["SHIP VALUE"] = pd.to_numeric(newfile["SHIP VALUE"],errors = 'coerce')

    df = newfile.groupby("YEAR")["SHIP VALUE"].mean()

    fig,ax = plt.subplots()
    ax.plot(df.index,df.values)
    ax.set_xlabel('Year')
    ax.set_ylabel('Average Ship Value ($)')
    ax.set_title('Average Ship Values In Different Years')

    st.pyplot(fig)
    with st.expander("See explanation"):
        st.write("The chart above shows the line graph of average ship value in different years. Notice that some states may have empty linegraph since there's no recorded ship value.")



def main():
    tab1, tab2 = st.tabs(["Shipwreck in Different States of Departure", "Map and Utility"])
    with tab1:
        df = pd.read_csv('ShipwreckDatabase.csv')
        df['STATE'] = df["DEPARTURE PORT"].apply(getting_state)
        state_list = []
        for row in df.itertuples():
            if len(row[-1]) != 0 and row[-1] not in state_list: #clean up state_list to ensure no empty choice of selection will be on the sidebar
                state_list.append(row[-1].upper())

        state_info = st.sidebar.radio("Please select a state of departure to analyze:", state_list)
        st.title("Shipwreck Information in Different States")
        st.header("Descriptive Statistics")
        st.write(f"Here you will find basic statistics regarding the number of people loss for the vessels departed from {state_info}.")

        count, mean, minimum, maximum = stats(df,state_info)
        stats_rows = [
            ["Count:", f"{count:5.0f}"],
            ["Mean:", f"{mean:5.0f}"],
            ["Minimum:", f"{minimum:5.0f}"],
            ["Maximum:", f"{maximum:5.0f}"]]
        col_width = max(len(str(word)) for row in stats_rows for word in row) + 5  # padding
        for row in stats_rows:
            row_words = []
            for word in row:
                row_words.append(str(word).ljust(col_width))
            st.text("".join(row_words))

        st.write("-"*100)

        st.header("Scatterplot")
        st.caption("Below you'll find the information regarding the scatterplot of the :blue[number of lives loss] in each year")
        scatter_plot(state_info,df)

        st.write("-"*100)

        st.header("Horizontal Histogram")
        st.caption("Below you'll find the information regarding the horizontal histogram of the :blue[top 5 vessels that has the most shipwrecks] with the number of shipwrecks occurs")
        option = st.selectbox(
            'You may select below for the order of the bars in horizontal histogram',
            ('ascending', 'descending'))
        vessle_type(state_info, df, option)

        st.write("-"*100)
        st.header("Line Graph")
        st.caption("Below you'll find the :blue[average ship value in dollar] in different years")
        line_graph(state_info, df)


    with tab2:
        st.title("Shipwreck Location Demonstrated in a Map")
        st.caption("Below you'll find the :blue[location of the shipwrecks on a map]")
        map(df)
        st.write("-"*100)
        interact()


main()
