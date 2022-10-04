#
# Flask app dokrisation
# https://docs.docker.com/language/python/deploy/
# https://www.docker.com/blog/how-to-dockerize-your-python-applications/
#
FROM python:3.9

WORKDIR /home/app

COPY ./mentor-search.requirements.txt .

RUN pip3 install -r mentor-search.requirements.txt

#
# "bson" pakcage should not be installed as pymongo comes with its own
# https://stackoverflow.com/questions/60149801/import-error-importerror-cannot-import-name-abc-from-bson-py3compat
#
RUN pip3 install datetime
RUN pip3 install pandas
RUN pip3 install "pymongo[srv]"
RUN pip3 install waitress
RUN pip3 install Paste
RUN pip3 install flask-cors
RUN pip install flask-smorest

COPY . .

#ENV NODE_ENV='development'
#ENV APP_NAME='MapOut Skills'
#ENV PORT=5041
#ENV MONGODB_STAGING_URI='mongodb+srv://mapout:mapout@mapoutdb.hj2on.mongodb.net/mapout-staging?retryWrites=true&w=majority'
#ENV DATABASE='mapout-staging'
#ENV FLASK_APP='src/controllers/mentor-search/intelligent-search.py'
#ENV FLASK_DEBUG=1


EXPOSE 5041

#
# Must be used for deployment to any environemnt
#
ENTRYPOINT [ "python3", "src/controllers/mentor-search/production-server.py"]

#
# For local development
#
#CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5041"]
