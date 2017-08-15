CREATE TABLE wiki_stuff (
    id INTEGER,
    title TEXT
);

CREATE TABLE wiki_types (
    id INTEGER,
    type TEXT
);


CREATE TABLE stuff_to_type (
    id,
    stuff_id INTEGER,
    type_id TEXT
);
