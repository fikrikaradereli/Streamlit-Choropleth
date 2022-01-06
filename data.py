import streamlit as st
import pandas as pd
import json


COL_NAMES = ["Şehir", "Toplam", "Dolaşım Sistemi Hastalıkları", "İyi Huylu ve Kötü Huylu Tümörler", "Solunum Sistemi Hastalıkları", "Sinir Sistemi ve Duyu Organları Hastalıkları", "Endokrin (iç salgı bezi), Beslenme ve Metabolizmayla İlgili Hastalıklar", "Dışsal Yaralanmalar ve Zehirlenmeler", "Diğer Hastalıklar"]


@st.cache
def get_data():
    df = pd.read_excel('Daimi İkametgaha Göre Seçilmiş Ölüm Nedenlerinin Dağılımı.xls',
    skiprows=6, skipfooter=9, header=None
    )
    df = df.drop(df.columns[1:3], axis=1)

    dfs = {}

    for year in range(2009,2018):
        dfs[year] = df.iloc[:,0:9]
        dfs[year].columns = COL_NAMES
        df = df.drop(df.columns[1:10], axis=1)

    for k,v in dfs.items():
        dfs[k].iloc[0,0] = 'Türkiye'

    population_df = pd.read_excel('Yıllara Göre İl Nüfusları.xls', skiprows=3, skipfooter=8)

    population_df.drop(population_df.columns[1:11], axis=1, inplace=True)
    population_df.drop(population_df.columns[-3:], axis=1, inplace=True)
    population_df.rename(columns={'Unnamed: 0':'Şehir'}, inplace=True)

    population_df.iloc[0,0] = 'Türkiye'

    for k,v in dfs.items():
        dfs[k] = dfs[k].merge(population_df[['Şehir', k]], how='inner', on='Şehir')
        dfs[k].columns = [*dfs[k].columns[:-1], 'Nüfus'] # Pek anlamadım ama son sütun ismini değiştiriyor.

    return dfs


@st.cache
def get_geojson():
    with open('./tr-cities.json', encoding="utf-8") as response:
        geo_json = json.load(response)

    geo_json["features"][2]['properties']['name'] = 'Afyonkarahisar' # GeoJson'da Afyon diye isimlendirilmiş. Düzelttik.

    #for i in range(len(geo_json["features"])):
    #    print(geo_json["features"][i]['properties']['name'])

    return geo_json