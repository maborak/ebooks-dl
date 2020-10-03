FROM python:3.7.3-slim
COPY src/ /src
RUN pip install -r /src/requirements.txt
WORKDIR /src
COPY docker-entrypoint.sh /
ENV PORT ${PORT:-5000}
ENTRYPOINT ["sh", "/docker-entrypoint.sh"]
EXPOSE $PORT
#CMD uvicorn rest:app --reload --host=0.0.0.0 --header="build-time: ${BUILD_DATE}"  --header="server: maborak" --port=$PORT
CMD uvicorn rest:app --reload --host=0.0.0.0 --port=$PORT --header="asddd:maborak"
