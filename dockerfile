FROM python:latest
WORKDIR /app
COPY main.py /app
RUN pip install websockets
RUN pip install pandas
EXPOSE 6000
CMD ["python", "./main.py"]