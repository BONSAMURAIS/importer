FROM python:3.12-slim


RUN pip3 install appdirs==1.4.4 \
docopt==0.6.2 \
rdflib==7.6.0 \
requests==2.33.0 \
SPARQLWrapper==2.0.0

COPY ./bonsai_seeder /bonsai_seeder
COPY ./setup.py /setup.py
COPY ./LICENSE /LICENSE
COPY ./README.md /README.md

RUN pip3 install .

RUN mkdir /data
VOLUME /data

ENTRYPOINT ["bseeder"]
CMD ["-h"]
