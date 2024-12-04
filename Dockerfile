FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /django

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN chmod +x /django/entrypoint.sh
ENTRYPOINT ["/django/entrypoint.sh"]


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]