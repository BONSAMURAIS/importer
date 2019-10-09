FROM python:3.7-buster


RUN pip3 install appdirs==1.4.3 \
docopt==0.6.2 \
rdflib==4.2.2 \
requests==2.22.0 \
SPARQLWrapper==1.8.4

COPY ./bonsai_seeder /bonsai_seeder
COPY ./setup.py /setup.py
COPY ./LICENSE /LICENSE
COPY ./README.md /README.md

RUN python setup.py install

RUN mkdir /data
VOLUME /data

ENTRYPOINT ["bseeder"]
CMD ["-h"]


