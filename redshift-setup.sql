create schema brightwheel_external;
create schema brightwheel_staging;

create user airflow with password 'awfasi343a!!LDF'
    nocreatedb nocreateuser syslog access restricted
    connection limit 10;

-- create airflow group
create group airflow with user airflow;

-- grants on brightwheel_external schema
grant usage on schema brightwheel_external to group airflow;
grant create on schema brightwheel_external to group airflow;
grant all on all tables in schema brightwheel_external to group airflow;

-- grants on brightwheel_staging schema
grant usage on schema brightwheel_staging to group airflow;
grant create on schema brightwheel_staging to group airflow;
grant all on all tables in schema brightwheel_staging to group airflow;

-- reassign schema ownership to airflow
alter schema brightwheel_staging owner to airflow;
alter schema brightwheel_external owner to airflow;