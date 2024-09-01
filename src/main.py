import pandas as pd
import plotly.express as px
import requests


def treemap(save_img: bool = False):
    response = requests.get(
        "https://coin360.com/site-api/coins?currency=USD&period=24h&ranking=top100"
    ).json()

    # Get the categories
    categories: dict = response["categories"]

    # Flatten the data to repeat rows for each category in 'ca'
    expanded_data = []

    for entry in response["data"]:
        # Determine the categories to use
        category_list = entry.get("ca", ["Others"])

        for category in category_list:
            new_entry = entry.copy()
            new_entry["ca"] = categories.get(category, {"title": "Others"})["title"]
            expanded_data.append(new_entry)

    # Create a dataframe from the expanded data
    df = pd.DataFrame(expanded_data)

    # Create custom text that includes the name, percentage change, and price
    df["text"] = (
        '<span style="font-size:20px"><b>'
        + df["s"]
        + "</b></span>"  # Name in larger font and bold
        + "<br>"
        + '<span style="font-size:16px">'
        + "$"
        + df["p"].round(2).astype(str)
        + "</span>"  # Price in smaller font
        + "<br>"
        + '<span style="font-size:16px">'
        + df["ch"].round(2).astype(str)
        + "%</span>"  # Percentage change in smaller font
    )
    # Create the treemap
    fig = px.treemap(
        df,
        path=["ca", "n"],  # Divide by category and then by coin name
        values="mc",  # The size of each block is determined by market cap
        color="ch",  # Color by the percentage change in price
        hover_data=["p", "v", "ts"],  # Information to show on hover
        color_continuous_scale=[
            (0, "#ed7171"),  # Bright red at -5%
            (0.5, "grey"),  # Grey around 0%
            (1, "#80c47c"),  # Bright green at 5%
        ],
        range_color=(-1, 1),
        color_continuous_midpoint=0,
        custom_data=["text"],  # Provide the custom text data for display
    )

    # Removes background colors to improve saved image
    fig.update_layout(
        margin=dict(t=30, l=10, r=10, b=10),
        font_size=20,
        coloraxis_colorbar=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # Adjust the layout for better visualization of the text
    fig.update_traces(
        texttemplate="%{customdata[0]}",  # Use the custom HTML-styled data for the text template
        textposition="middle center",  # Center the text in the middle of each block
        textfont=dict(color="white"),  # Set all text color to white
        marker=dict(
            line=dict(color="black", width=1)
        ),  # Add a black border around each block for better visibility
    )

    # Disable the color bar
    fig.update(layout_coloraxis_showscale=False)

    # Save the figure as an image
    # Increase the width and height for better quality
    if save_img:
        fig.write_image(file="img/treemap.png", format="png", width=1920, height=1080)

    # Show the treemap
    fig.show()


if __name__ == "__main__":
    treemap(save_img=False)
