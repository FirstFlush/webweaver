import pandas as pd


async def outfile_hook(dataframes:dict[str, pd.DataFrame]):
    """Flattens GoogleMapsCompany and GoogleMapsReview into a single table."""
    df_company = dataframes['GoogleMapsCompany']
    df_review = dataframes['GoogleMapsReview']
    df_google = df_company.merge(df_review, left_on="id", right_on="company_id", how="left")
    df_google.drop(columns=['id_x', 'id_y', 'company_id'], inplace=True)

    dataframes = {'GoogleMaps':df_google}

    return dataframes