#FROM nikolaik/python-nodejs:python3.9-nodejs14-alpine
FROM nikolaik/python-nodejs:python3.9-nodejs14

WORKDIR /home/app

COPY . .

RUN pip3 install -r requirements.txt
RUN pip3 install pandas

ENV CI=true
RUN npm ci

EXPOSE 4041

ENTRYPOINT ["npm", "run", "start"]
