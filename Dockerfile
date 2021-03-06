FROM python:3.7.3-slim
COPY ebooksdl/ /ebooksdl
COPY requirements.txt /ebooksdl/requirements.txt
RUN pip install -r /ebooksdl/requirements.txt
WORKDIR /
COPY docker-entrypoint.sh /
ENV PORT ${PORT:-5000}
ENTRYPOINT ["sh", "/docker-entrypoint.sh"]
ENV BUILD_DATE ${BUILD_DATE:-none}
EXPOSE $PORT
# CMD uvicorn rest:app --reload --host=0.0.0.0 --header="build-time: ${BUILD_DATE}"  --header="server: maborak" --port=$PORT
CMD uvicorn ebooksdl.rest:app --debug --host=0.0.0.0 --port=$PORT --header="Server:maborak" --header="build-time:${BUILD_DATE}"
