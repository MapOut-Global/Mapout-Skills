#
# Python with Node.js bundled images
# https://hub.docker.com/r/nikolaik/python-nodejs
#
FROM nikolaik/python-nodejs:python3.9-nodejs14

WORKDIR /home/app

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt
RUN pip3 install pandas

RUN python -m nltk.downloader all

COPY ./package*.json .

ENV CI=true
RUN npm ci

COPY . .

EXPOSE 4041

CMD ["npm", "run", "start"]
