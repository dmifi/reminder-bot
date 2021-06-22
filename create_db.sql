create DATABASE reminderbot
    with
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Russian_Russia.1251'
    LC_CTYPE = 'Russian_Russia.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

create TABLE client(
    id integer primary key,
    telegram_id integer,
    telegram_firstname varchar(255),
    telegram_username varchar(255)
    CONSTRAINT telegram_id UNIQUE (telegram_id)
);

create TABLE task(
    id integer primary key,
    description text,
    created timestamp without time zone,
    completed timestamp without time zone,
    done boolean,
    client_id integer foreignkey(client.id)
);