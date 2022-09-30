#
# Python with Node.js bundled images
# https://hub.docker.com/r/nikolaik/python-nodejs
#
FROM nikolaik/python-nodejs:python3.9-nodejs14

WORKDIR /home/app

COPY . .

RUN pip3 install -r requirements.txt
RUN pip3 install pandas

ENV CI=true
RUN npm ci

EXPOSE 4041

ENTRYPOINT ["npm", "run", "start"]
