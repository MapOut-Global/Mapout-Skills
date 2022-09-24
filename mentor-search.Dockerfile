#FROM nikolaik/python-nodejs:python3.9-nodejs14-alpine
FROM python:3.9

WORKDIR /home/app

COPY . .

RUN pip3 install -r mentor-search.requirements.txt
# RUN pip3 install json bson datetime pandas

# "bson" pakcage should not be installed as pymongo comes with its own
# RUN pip3 install bson datetime pandas

RUN pip3 install datetime pandas "pymongo[srv]" waitress Paste

ENV NODE_ENV='development'
ENV APP_NAME='MapOut Skills'
ENV PORT=5041
ENV MONGODB_STAGING_URI='mongodb+srv://mapout:mapout@mapoutdb.hj2on.mongodb.net/mapout-staging?retryWrites=true&w=majority'
ENV DATABASE='mapout-staging'
ENV FLASK_APP='src/controllers/mentor-search/intelligent-search.py'


EXPOSE 5041

# ENTRYPOINT [ "python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5041"]
ENTRYPOINT [ "python3", "src/controllers/mentor-search/production-server.py"]
