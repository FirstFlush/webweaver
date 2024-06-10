import pandas as pd
from scraping_modules.eventseye.models import (
    EventsEyeTradeShow, 
    # EventsEyeIndustry, 
    # EventsEyeOrganizer, 
    # EventsEyeVenue
)
from common.utils import instance_to_dict


async def outfile_hook(dataframes:dict[str, pd.DataFrame]):
    """Flattens EventsEye tables into single table."""
    data = []

    trade_shows = await EventsEyeTradeShow.all().prefetch_related('venue')#, 'organizers', 'industries')
    for trade_show in trade_shows:
        trade_show_data = {
            'EventName': trade_show.event_name,
            'Description': trade_show.description,
            'Audience': trade_show.audience,
            'Cycle': trade_show.cycle,
            'Email': trade_show.email,
            'Website': trade_show.website,
            'Date': trade_show.date,
            'Duration': trade_show.duration_days,
            'Venue': trade_show.venue.venue_name,
            'City': trade_show.venue.city,
            'Country': trade_show.country
        }

        # print(trade_show_data)
        # print()
        data.append(trade_show_data)
    df = pd.DataFrame(data)
    # df.drop(columns=["id"])
    return {"Fiverr":df}



    # df_merged = pd.merge(df_events, df_venues, left_on="venue_id", right_on="id", how="left")
    # df_merged.drop(columns=['id_x', 'venue_id', 'id_y'], inplace=True)
    # country_col = df_merged.pop('country')
    # df_merged.insert(12, 'country', country_col)
    # return {"Blahh":df_merged}

    # df_company = dataframes['GoogleMapsCompany']
    # df_review = dataframes['GoogleMapsReview']
    # df_google = df_company.merge(df_review, left_on="id", right_on="company_id", how="left")
    # df_google.drop(columns=['id_x', 'id_y', 'company_id'], inplace=True)

    # dataframes = {'GoogleMaps':df_google}

    # return dataframes



    # events = await EventsEyeTradeShow.all().prefetch_related('organizers')
    # data = []
    # for event in events:
    #     for organizer in event.organizers:
    #         row = {
    #             'event_name': event.event_name,
    #             'organizer_name': organizer.organizer_name
    #         }
    #         data.append(row)
    # df = pd.DataFrame(data)
    # return {'Events':df}