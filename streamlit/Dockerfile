FROM ymlai87416/python_talib:python3.8_0.4_2
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN mkdir /app/.streamlit
RUN mkdir /app/pages
EXPOSE 80

#COPY config.py /app
COPY streamlit_app.py /app
COPY pages/香港期權排序.py /app/pages
COPY pages/香港期權變化.py /app/pages
COPY pages/SPX_option_study.py /app/pages
COPY pages/Portfolio.py /app/pages
COPY .streamlit/config.toml /app/.streamlit


ENTRYPOINT ["streamlit", "run"]

CMD ["streamlit_app.py"]