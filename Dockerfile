FROM python:3-onbuild

ADD start.sh start.sh
RUN chmod +x start.sh

CMD ./start.sh 0.0.0.0:9000