FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
ENV FLASK_APP=secure-sms.app.__init__
EXPOSE 8000
CMD ["gunicorn","-w","2","-b","0.0.0.0:8000","run:app"]