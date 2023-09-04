FROM python:latest

WORKDIR /ws2g
COPY . /ws2g

RUN python -m pip install --upgrade pip

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN /root/.local/bin/poetry build
RUN pip install dist/$(ls dist | grep .*.whl)

WORKDIR /
RUN git clone https://github.com/arazi47/built-to-serve-testing-app.git testing-app
WORKDIR /testing-app

EXPOSE 8000
CMD ["python", "main.py"]