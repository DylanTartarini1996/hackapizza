import pandas as pd


def transform_distance_matrix(df):
    """
    Transform a distance matrix DataFrame into a long format with 'From', 'To', and 'Distance' columns.

    Parameters:
    df (pandas.DataFrame): Input distance matrix with planets as both index and columns

    Returns:
    pandas.DataFrame: Long format DataFrame with columns ['From', 'To', 'Distance']
    """
    df = df.reset_index()

    df = df.rename(columns={'/': 'From'})

    # Melt the DataFrame to get it into long format
    melted_df = pd.melt(
        df,
        id_vars=['From'],
        var_name='To',
        value_name='Distance'
    )

    # Filter out self-distances (where Distance = 0)
    result = melted_df[melted_df['Distance'] > 0]

    # Reset index and sort by From and To
    result = result.sort_values(['From', 'To']).reset_index(drop=True)

    return result

if __name__ == "__main__":
    df_distances = pd.read_csv('../HackapizzaDataset/Misc/Distanze.csv')
    df_distances_transformed = transform_distance_matrix(df_distances)

    df_distances_transformed.to_csv("distanze_transformed.csv", index=False)

