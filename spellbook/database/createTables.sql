CREATE TABLE IF NOT EXISTS "subclass" (
	"id"            INTEGER NOT NULL UNIQUE,
	"subclass"      TEXT NOT NULL UNIQUE,
	"isSavant"   	INTEGER NOT NULL,
	"isValid"		INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "player" (
	"id"				INTEGER NOT NULL UNIQUE,
	"discord_id"		INTEGER NOT NULL,
	"char_name"			TEXT NOT NULL,
	"wizard_subclass"	INTEGER NOT NULL,
	"wizard_level"		INTEGER,
	"isActive"			INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
	FOREIGN KEY("wizard_subclass") REFERENCES "subclass"("id"),
	CONSTRAINT unqPlayerChar UNIQUE(discord_id, char_name)
);

CREATE TABLE IF NOT EXISTS "spell" (
	"id"			INTEGER NOT NULL UNIQUE,
	"name"			TEXT NOT NULL UNIQUE,
	"school"		TEXT NOT NULL,
	"level"			INTEGER NOT NULL,
	"isRitual"      INTEGER NOT NULL,
	"isDunamancy"	INTEGER NOT NULL DEFAULT 0,
	"isValid"		INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "player_spell" (
	"id"		INTEGER NOT NULL UNIQUE,
	"player"	INTEGER NOT NULL,
	"spell"		INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("player") REFERENCES "player"("id"),
	FOREIGN KEY("spell") REFERENCES "spell"("id"),
	UNIQUE("player","spell")
);