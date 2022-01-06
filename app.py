import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_disqus import st_disqus

from data import get_data, get_geojson

def config():
    st.set_page_config(
        page_title='Türkiye\'de Ölüm Nedenleri',
        page_icon="🇹🇷",
        layout="wide"
    )

    hide_menu_style = """
                        <style>
                        #MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}
                        footer:after { content:'Fikri Karadereli tarafından geliştirildi.'; visibility: visible; display: block; margin-bottom: 10px; color:#fafafa99; font-size:14px;}
                        </style>
                    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


def main():
    data = get_data()
    geo_json = get_geojson()

    reasons = data[2017].columns.to_list()[1:-1]
    years = sorted(list(data.keys()), reverse=True)
    
    st.title('TÜRKİYE\'DE ÖLÜM NEDENLERİ')

    # sidebar
    year = st.sidebar.selectbox(
        'Yılı burdan değiştirebilirsiniz',
        years
    )

    reason = st.sidebar.selectbox(
        'Ölüm nedenini burdan değiştirebilirsiniz',
        reasons
    )

    crude_mortality_rates = ((data[year][reason] / data[year]['Nüfus']) * (10**6)).astype('int')
    crude_mortality_rates.name = 'Kaba Ölüm Hızı (100 binde)'
    
    rates_df = pd.concat([data[year]['Şehir'], crude_mortality_rates], axis=1)
    # rates_df.drop(0, inplace=True) # Remove Türkiye

    reason_text =  f'{reason} Nedeniyle' if reason != 'Toplam' else ''
    map_title = f'{year} - İllere Göre {reason_text} Ölüm Hızları'

    fig = go.Figure(data=go.Choropleth(locations=data[year]['Şehir'],
                                    z = rates_df['Kaba Ölüm Hızı (100 binde)'], # Data to be color-coded
                                    geojson=geo_json,
                                    featureidkey="properties.name",
                                    
                                    colorbar_title = 'Kaba Ölüm Hızı<br><i>(100 bin kişide)</i>',
                                    colorscale='viridis_r',
                                    ))

    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0},
                    geo_scope='asia', 
                    modebar_remove=['select', 'lasso', 'pan', 'zoomIn', 'zoomOut'],
                    title_text=map_title)
    fig.update_geos(fitbounds="locations", visible=False)
    
    st.plotly_chart(fig, use_container_width=True)
    st.write('')

    # Bar Chart
    df = rates_df.sort_values(by='Kaba Ölüm Hızı (100 binde)', ascending=False)[:5]

    x = df['Şehir']
    y = df['Kaba Ölüm Hızı (100 binde)']

    bar_fig = go.Figure([go.Bar(x=x, y=y, text=y, textposition='auto')])
    bar_fig.update_layout(
                        title=f'{reason_text} Ölüm Hızı En Yüksek 5 Şehir <i>({year})</i>', 
                        xaxis_title='Şehirler', yaxis_title='Ölüm Hızı <i>(100 binde)</i>', 
                        modebar_remove=['select', 'lasso', 'pan', 'zoom', 'zoomIn', 'zoomOut', 'autoscale'],
    )
    bar_fig.update_traces(hoverinfo='skip')

    st.plotly_chart(bar_fig, use_container_width=True)

    # Pie Chart
    city = df.iloc[0,0]
    population = data[year][data[year]['Şehir'] == city].iloc[0,-1]
    df = data[year][data[year]['Şehir'] == city].iloc[:,2:-1]
    rates = ((df / population) * (10**6)).astype('int')

    pie_fig = go.Figure(data=[go.Pie(labels=list(rates.columns), values=list(rates.values[0]))])
    pie_fig.update_layout(
                        title=f'{city} Şehrindeki Tüm Ölüm Hızları <i>({year})</i>', 
                        modebar_remove=['select', 'lasso', 'pan', 'zoom', 'zoomIn', 'zoomOut', 'autoscale'],
                        legend_font_size = 14,
    )
    st.plotly_chart(pie_fig, use_container_width=True)

    st.write('*Dilerseniz yorum bırakabilirsiniz.*')
    st_disqus('turkiyede-olum-nedenleri')
    st.write('----')
    st.write('''
            ##### Veri Kaynağı
            ###### TÜİK  
            - [Daimi İkametgaha Göre Seçilmiş Ölüm Nedenlerinin Dağılımı](https://data.tuik.gov.tr/Bulten/DownloadIstatistikselTablo?p=lpXMRoJZDYpN67YPv1rihb/9YIQJMRQCvmPzrACvQVPOzM48UsvFTKAqmQIQxJXL)  
            - [Yıllara Göre İl Nüfusları](https://data.tuik.gov.tr/Bulten/DownloadIstatistikselTablo?p=O2zBYGxP8Xq7B/ewq0RTzhxgOygTDI72NMGjZ8ZsvIRm2WaeYIHkorN3SRh5qmcJ)  
            ###### GeoJSON  
            - [GeoJson](https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json)
            '''
    )

if __name__ == "__main__":
    config()
    main()