FROM postgres:15

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=mydb

# Copy the init.sql file to the /docker-entrypoint-initdb.d/ directory.
COPY init.sql /docker-entrypoint-initdb.d/
RUN chmod 644 /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
