import datetime
import numpy as np
import pandas as pd
import db_tools.db_operations as db_operations


def read_site_titles(scrape_key):

    conn = db_operations.db_connect('raw')

    sql_titles = 'SELECT * FROM titles WHERE fk_scrapes = ' + str(scrape_key)
    sql_scrape = 'SELECT * FROM scrapes WHERE pk_scrapes = ' + str(scrape_key)

    raw_titles = db_operations.execute_sql(conn, sql_titles)
    scrape = db_operations.execute_sql(conn, sql_scrape)

    site_titles = [title_item[2]
                   for title_item in raw_titles
                   if title_item[1] == scrape_key]

    db_operations.db_close(conn)

    return site_titles, scrape[0]


def read_all():

    conn = db_operations.db_connect('processed')

    sql = '''SELECT * FROM words'''
    data = db_operations.execute_sql(conn, sql)

    df = pd.DataFrame(data,
                      columns=['key1', 'scrape_key', 'site', 'dt',
                               'tm', 'word', 'freq', 'rank'])

    db_operations.db_close(conn)

    df['dtm'] = df.dt + " " + df.tm
    df['dtm'] = pd.to_datetime(df['dtm'])

    df = df[df.groupby(['dtm'])['tm'].transform(max) == df['tm']]

    return df


def trunc_df_days(df, start_day, end_day):
    #day_delta = str(how_many_days) + "day"
    return df[(df.dtm >= start_day) & (df.dtm <= end_day)]


def transform_data(df,
                   how_many_words_trend,
                   how_many_words_top,
                   start_day,
                   end_day,
                   interval):

    # TODO: this function should be broken down into multipl smaller functions

    trend_data = {}
    top_data = {}

    df = trunc_df_days(df, start_day, end_day)

    if interval == 'hourly':
        pivot_by = 'dtm'
        num_of_scrapes = df.groupby('dtm')['scrape_key'].nunique()
    else:
        pivot_by = 'dt'
        num_of_scrapes = df.groupby('dt')['scrape_key'].nunique()

    df = pd.pivot_table(df,
                        index=['word'],
                        columns=[pivot_by],
                        values='freq',
                        aggfunc=np.sum)

    df = df.divide(num_of_scrapes, axis=1)

    df = df.fillna(0)

    ser = df.mean(axis=1).sort_values(ascending=False)[:how_many_words_top]

    ser = ser.map(lambda x: round(x, 6) * 100)

    top_data['labels'] = list(ser.index)
    top_data['values'] = list(ser)

    df['total'] = df.sum(axis=1)
    df = df.sort_values(by='total', ascending=False).drop(['total'], axis=1)

    df = df.iloc[:how_many_words_trend, :]

    dtms = list(df.columns)
    trend_data['time_dim'] = [str(dtm)[:16] for dtm in dtms]

    trend_data['words'] = list(df.index)

    value_list = []
    for i in range(0, how_many_words_trend):
        vals = df.iloc[i, :]
        vals = map(lambda x: round(x, 6) * 100, vals)
        value_list.append(list(vals))

    trend_data['value_list'] = value_list

    return trend_data, top_data


def get_app_load_data(trend_words, top_words, hourly_days, daily_days):

    app_load_data = {}
    app_load_data['hourly'] = {}
    app_load_data['daily'] = {}

    df = read_all()

    date_ranges_hourly = [['2020-06-08', datetime.datetime(2020, 6, 8, 0, 1), datetime.datetime(2020, 6, 15, 0, 1)],
                          ['2020-06-15', datetime.datetime(2020, 6, 15, 0, 1), datetime.datetime(2020, 6, 22, 0, 1)],
                          ['latest', datetime.datetime(2020, 6, 18, 0, 1), datetime.datetime(2020, 6, 25, 0, 1)]]

    start_day_daily = datetime.datetime(2020, 6, 1, 0, 1)
    end_day_daily = datetime.datetime(2020, 6, 30, 0, 1)

    for daterange in date_ranges_hourly:

        app_load_data['hourly'][daterange[0]] = {}

        app_load_data['hourly'][daterange[0]]['trend_data_hourly'], \
            app_load_data['hourly'][daterange[0]]['top_words_hourly'] = transform_data(df,
                                                                         trend_words,
                                                                         top_words,
                                                                         daterange[1],
                                                                         daterange[2],
                                                                         'hourly')

    app_load_data['daily']['latest'] = {}

    app_load_data['daily']['latest']['trend_data_daily'], \
        app_load_data['daily']['latest']['top_words_daily'] = transform_data(df,
                                                          trend_words,
                                                          top_words,
                                                          start_day_daily,
                                                          end_day_daily,
                                                          'daily')

    return app_load_data



