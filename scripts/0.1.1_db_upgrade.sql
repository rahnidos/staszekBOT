CREATE TABLE "areas" (
	"name"	TEXT,
	"maxlat"	REAL,
	"maxlong"	REAL,
	"minlat"	REAL,
	"minlong"	REAL,
	"w"	INTEGER,
	PRIMARY KEY("name")
);
INSERT INTO "main"."commands" ("alias", "real", "type") VALUES ('where', 'rollLocation', '1');
