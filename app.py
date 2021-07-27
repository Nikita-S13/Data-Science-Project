import multi_page_scraper as mps
import streamlit as st
from database import Review
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pandas as pd
import os
import review_scaper as rs
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
st.set_page_config(layout='wide')
pd.set_option('display.expand_frame_repr', False)

def opendb():
    engine = create_engine('sqlite:///db.sqlite3') # connect
    Session =  sessionmaker(bind=engine)
    return Session()

def load_from_database():
    db = opendb()
    results = db.query(Review).all()
    db.close()
    return results

st.title("sentiment analysis on products using web scraping")
st.header("Scrape products")

with st.beta_expander("show contents"):

    url = "https://www.flipkart.com/search?"
    search_term = st.text_input("enter a product category to search")
    output_area = st.empty()

    if st.button("start scraper") and search_term:
        page = 1
        filename = f'scraped_data/product_{search_term}.csv'

        scraped_products = [] 
        with st.spinner("loading"):
            while True:
                starturl = f"{url}q={search_term}&page={page}"
                output_area.info(f'getting data from {starturl} ...')
                soup = mps.get(starturl)
                if not soup:
                    output_area.info('scraper closed')
                    break
                else:
                    output = mps.extract(soup)
                    if len(output) == 0:
                        output_area.info('scraper closed')
                        break
                    scraped_products.extend(output)
                    output_area.info(f'total size of collected data {len(scraped_products)}')
                    page += 1

            # save the stuff
            file = mps.save(scraped_products,filename)
            st.balloons()
        if file:
            st.success(f"products data saved in {file}") 

st.header("Scrape products reviews")
with st.beta_expander("show scraping options"):
    files = os.listdir("scraped_data")
    files = [os.path.join("scraped_data",file) for file in files if file.endswith(".csv")]
    file = st.selectbox("select a product", files)
    df = pd.read_csv(files)
    limit = st.slider("select number of products to scraped review from",1,len(df),10)
    if st.button("scraped reviews"):
        with st.spinner("scraping"):
            dataset = rs.get_reviews(df,limit)
            db = opendb()
            for row in dataset:
                db.add(Review(**row))
            db.commit()
            st.balloons()
            db.close()
st.header("Display Sentiment")
with st.beta_expander("show results"):
    db = opendb()
    results = db.query(Review).all()
    df = pd.read_sql(db.query(Review).statement, db.bind)
    st.dataframe(df)

    st.header("general sentiment visualization")
    # sentiment analysis
    if st.checkbox("raw sentiment data"):
        st.dataframe(df.groupby('product')['sentiment'].sum())
    product_sentiment_df =df.groupby('product')['sentiment'].sum().reset_index()
    fig =px.bar(product_sentiment_df,x='sentiment',y=product_sentiment_df.index,color='sentiment',hover_data=['product'],orientation='h',title='Product sentiment  sum')
    st.plotly_chart(fig,use_container_width=True)     
    
    if st.checkbox("raw product sentiment mean data"):
        st.dataframe(df.groupby('product')['sentiment'].mean().reset_index())
    product_sentiment_avg_df =df.groupby('product')['sentiment'].mean().reset_index()
    fig =px.scatter(product_sentiment_avg_df,x='sentiment',y=product_sentiment_avg_df.index,color='sentiment',hover_data=['product'],orientation='v',title='Product sentiment average',size='sentiment')
    st.plotly_chart(fig,use_container_width=True)    
    
    if st.checkbox("raw product count data"):
        st.dataframe(df.groupby('product')['product'].count())
    product_count_df = df.groupby('product')['product'].count()
    fig =px.bar(product_count_df,x='product',y='product',color='product',hover_data=[product_count_df.index],orientation='h',title='Product review count')
    st.plotly_chart(fig,use_container_width=True)

    # if st.checkbox("show sentiment distribution"):
    fig,ax =plt.subplots()
    sns.distplot(df['sentiment'], bins=20, kde=True, rug=True,ax=ax)
    ax.set_title("show sentiment distribution")
    st.pyplot(fig,use_container_width=True)

    fig,ax =plt.subplots(figsize=(15,10))
    sns.violinplot(y='sentiment',x='product',data=df,ax=ax,)
    plt.xticks(rotation=90)
    st.pyplot(fig,use_container_width=True)
    
    st.header("product wise sentiment visualization")
    product = st.selectbox("select a product",df['product'].unique().tolist())
    product_df = df[df['product']==product]
    if st.checkbox("show product raw data"):
        st.dataframe(product_df)
    
    fig,ax =plt.subplots()
    sns.distplot(product_df['sentiment'], bins=20, kde=True, rug=True,ax=ax)
    st.pyplot(fig,use_container_width=True)

    fig,ax =plt.subplots()
    sns.violinplot(product_df['sentiment'],ax=ax,)
    st.pyplot(fig,use_container_width=True)

    fig,ax =plt.subplots()
    product_df.groupby('sentiment_name')['sentiment'].count().plot(kind='pie',ax=ax,autopct='%1.1f%%',legend=True,title=f"{product} sentiment distribution",labels=None,wedgeprops={'edgecolor':'black','width':.5 })
    st.pyplot(fig,use_container_width=True)

    db.close()