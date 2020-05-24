import pandas as pd 
import numpy as np 
import os
from datetime import timedelta

import dl 

class Covid19SL():

    def __init__(self):
        dataDL = dl.Covid19DL()
        self.data = dataDL.getAllTargetData()

    def getData(self):
        dataDL = dl.Covid19DL()
        return dataDL.getAllTargetData()

    def getIndividualData(self, data):
        """
        returns dataframes of covid-19 data as: 
        df_jhu, df_nytimes_county, df_covidtracking_country, df_covidtracking_state, df_dxy_region, df_dxy_Country
        """

        df_jhu = data['JHU']['ProvinceState']
        df_nytimes_county = data['NyTimes']['County']
        df_covidtracking_country = data['CovidTracking']['CountryHistorical']
        df_covidtracking_state = data['CovidTracking']['StateHistorical']
        df_dxy_region = data['DxyCovid19']['Region']
        df_dxy_Country = data['DxyCovid19']['Country']

        return df_jhu, df_nytimes_county, df_covidtracking_country, df_covidtracking_state, df_dxy_region, df_dxy_Country
    
    def getListOfCountries(self, df_jhu):
        countries = np.append(df_jhu.CountryRegion.unique(), ['China'])
        return countries

    def getMetrics(self):
        return ['Active', 'Confirmed', 'Deaths', 'Recovered']

    def getDataByCountry(self, data, country, yAxisMetric, yAxisType):
        df_jhu, df_nytimes_county, df_covidtracking_country, df_covidtracking_state, df_dxy_region, df_dxy_Country = self.getIndividualData(data)

        df_china = pd.DataFrame(columns=['Confirmed', 'Deaths', 'Recovered', 'Latitude', 'Longitude', 'US_County', 'Active', 'CountryRegion', 'StateProvince'])

        df_china['Confirmed'] = df_dxy_Country.confirmed 
        df_china['Deaths'] = df_dxy_Country.death
        df_china['Recovered'] = df_dxy_Country.recovered
        df_china['CountryRegion'] = 'China'
        df_china['LastUpdateDatetime'] = pd.to_datetime(df_dxy_Country.date, unit='ns') - timedelta(days=1)
        df_china['LastUpdateDate'] = df_china.LastUpdateDatetime
        df_china = df_china[pd.to_datetime(df_china.LastUpdateDate, unit='ns').dt.strftime("%m/%d/%Y") != "04/23/2020"]
        df_china.LastUpdateDatetime = df_china.LastUpdateDatetime.astype(str)
        df_china.LastUpdateDate = df_china.LastUpdateDate.astype(str)

        df_world = df_jhu.append(df_china)

        df_world['LastUpdateDate'] = pd.to_datetime(df_world['LastUpdateDate'], unit='ns').dt.date
        df_world = df_world[pd.to_datetime(df_world.LastUpdateDate, unit='ns').dt.strftime("%m/%d/%Y") != "04/23/2020"]

        if country:
            df_filtered = df_world[df_world.CountryRegion == country].set_index(['CountryRegion', 'LastUpdateDate'])\
                .groupby(['CountryRegion', 'LastUpdateDate'])\
                .sum()\
                .reset_index()
        else:
            df_filtered = df_world.set_index(['LastUpdateDate'])\
                .groupby(['LastUpdateDate'])\
                .sum()\
                .reset_index()

        chart_basic = {
            'data': [dict(
                x = df_filtered.LastUpdateDate,
                y = df_filtered[yAxisMetric],
                text = df_filtered['CountryRegion'] if country else df_filtered.LastUpdateDate,
                mode = 'markers',
                marker = {
                    'size': 10,
                    'opacity': 0.5,
                    'line': {'width': 0.5, 'color': 'red'}
                }
            )],
            'layout': dict(
                xaxis = {
                    'title': 'Date',
                    'type': 'date'
                },
                yaxis = {
                    'title': yAxisMetric,
                    'type': 'linear' if yAxisType == 'Linear' else 'log'
                },
                margin = {'l': 40, 'b': 40, 't': 10, 'r': 0},
                hovermode = 'closest'
            )
        }

        df_pctChange = df_filtered[-21::]
        chart_pctChange = {
            'data': [dict(
                x = df_pctChange.LastUpdateDate,
                y = df_pctChange[yAxisMetric].pct_change() * 100,
                text = df_pctChange['CountryRegion'] if country else df_pctChange.LastUpdateDate,
                mode = 'lines+markers',
                marker = {
                    'size': 10,
                    'opacity': 0.5,
                    'line': {'width': 0.5, 'color': 'red'}
                }
            )],
            'layout': dict(
                xaxis = {
                    'title': 'Date',
                    'type': 'date'
                },
                yaxis = {
                    'title': '%s Percent Change' % yAxisMetric,
                    'type': 'linear'
                },
                margin = {'l': 40, 'b': 40, 't': 10, 'r': 0},
                hovermode = 'closest'
            )
        }
        
        return chart_basic, chart_pctChange
