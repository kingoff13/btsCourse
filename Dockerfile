FROM mysql:latest
ENV MYSQL_ROOT_PASSWORD=notalchemy
COPY dumps/dump.sql /docker-entrypoint-initdb.d/
