FROM python:3
ADD main.py /
RUN pip install websockets
EXPOSE 6000
CMD ["python", "./main.py"]