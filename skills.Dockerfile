#
# Python with Node.js bundled images
# https://hub.docker.com/r/nikolaik/python-nodejs
#
FROM nikolaik/python-nodejs:python3.9-nodejs14

WORKDIR /home/app

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt
RUN pip3 install pandas
RUN pip3 install openpyxl
RUN python3 -m spacy download en_core_web_sm
RUN python3 -m nltk.downloader all

COPY ./package*.json .

ENV CI=true
RUN npm ci

COPY . .

EXPOSE 4041

CMD ["npm", "run", "start"]
