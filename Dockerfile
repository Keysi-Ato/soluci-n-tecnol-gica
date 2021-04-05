
FROM odoo:10.0

USER root

RUN set -x
RUN apt-get update && apt-get dist-upgrade -y
RUN apt-get install -y --no-install-recommends python-dev \
    build-essential gcc libxml2-dev libxslt1-dev libssl-dev tesseract-ocr-eng \
    python-openssl python-imaging
RUN pip install setuptools==45.0.0 pip==20.0.2
RUN pip install lxml defusedxml bs4
RUN pip install cryptography cffi
RUN pip install ofxparse pyserial python-chart pyusb suds-jurko
RUN pip install ipaddress signxml pytesseract oca-decorators pysftp culqipy pymongo openupgradelib

USER odoo