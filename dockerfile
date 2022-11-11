FROM python:latest
ADD main.py /
RUN pip install websockets
RUN pip install pandas
EXPOSE 6000
CMD ["python", "./main.py"]