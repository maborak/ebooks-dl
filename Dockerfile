FROM python:3.7.3-slim
COPY src/ /src
RUN pip install -r /src/requirements.txt
WORKDIR /src
ENV PORT 5000
EXPOSE $PORT
CMD uvicorn rest:app --reload --host=0.0.0.0 --port=$PORT
