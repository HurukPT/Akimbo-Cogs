from curses import curs_set
import math
import sqlite3
import os.path
from os.path import exists
from . import customExceptions as error


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "WizardRepository.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)


def createDatabase():
    if not exists(DB_PATH):
        print("No Database found, creating a new one...")
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        sql_tables_script = open(os.path.join(
            BASE_DIR, "./database/createTables.sql"))
        sql_spells_script = open(os.path.join(
            BASE_DIR, "./database/insertData.sql"))
        try:
            cursor.executescript(sql_tables_script.read())
            cursor.executescript(sql_spells_script.read())
        except:
            print("Error while importing data into database")
        finally:
            cursor.close()


def connectDatabase():
    if not exists(DB_PATH):
        createDatabase()
    return sqlite3.connect(DB_PATH)


def addCharacter(discordId, charName, subclass, level):
    school = getSubclass(subclass)
    if not school:
        raise error.UnknownSubclass()
    isRitualCaster = str.lower(school) == "ritual caster"
    if isRitualCaster:
        level = 0
    try:
        level = int(level)
    except ValueError:
        raise error.InvalidCharacterLevel()
    if level < 1 or level > 20:
        raise error.InvalidCharacterLevel()
    currentChar = getPlayerCharacters(discordId, True)
    if currentChar:
        raise error.ActiveCharExists()
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"INSERT INTO 'player' VALUES(NULL, '{discordId}', '{charName}', '{school[0][0]}', '{level}', 1)"
        cursor.execute(query)
        db.commit()
    except sqlite3.IntegrityError:
        raise error.DuplicateCharacter()
    finally:
        cursor.close()
        db.close()


def retireCharacter(discordId):
    currentChar = getPlayerCharacters(discordId, True)
    if not currentChar:
        raise error.NoActiveCharacter()
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"UPDATE 'player' SET isActive = {False} WHERE discord_id = '{discordId}' AND isActive = {True}"
        cursor.execute(query)
        db.commit()
        return currentChar[0][2]
    finally:
        cursor.close()
        db.close()


def unretireCharacter(discordId, charName):
    currentChar = getPlayerCharacters(discordId, True)
    if currentChar:
        raise error.ActiveCharExists()
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"UPDATE 'player' SET isActive = {True} WHERE discord_id = '{discordId}' AND LOWER(char_name) = LOWER('{charName}') AND isActive = {False}"
        cursor.execute(query)
        db.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        db.close()


def getPlayerCharacters(discordId, isActive=True):
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"SELECT * FROM 'player' WHERE player.discord_id = {discordId}"
        if isActive:
            query += f" AND player.isActive = {isActive}"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()


def setLevelForPlayer(discordId, level):
    if not currentChar:
        raise error.NoActiveCharacter()
    try:
        level = int(level)
    except ValueError:
        raise error.InvalidCharacterLevel()
    currentChar = getPlayerCharacters(discordId, True)
    newLevel = currentChar[0][4] + level
    if (newLevel < 1 or newLevel > 20):
        raise error.InvalidCharacterLevel()
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"UPDATE 'player' SET wizard_level = {level} WHERE discord_id = {discordId} AND isActive = {True}"
        cursor.execute(query)
        db.commit()
    finally:
        cursor.close()
        db.close()


def getSpellListForPlayer(discordId):
    currentChar = getPlayerCharacters(discordId, True)
    if not currentChar:
        raise error.NoActiveCharacter()
    try:
        db = connectDatabase()
        cursor = db.cursor()
        if "Ritual Caster" not in currentChar:
            query = f"SELECT * FROM spell s WHERE s.isValid = {True} AND s.level <= {math.ceil(currentChar[4] / 2)} "
            if "Graviturgist" not in currentChar:
                query = query + f"AND isDunamancy = {False}"
        else:
            query = f"SELECT * FROM spell s WHERE s.isValid = {True} and s.isRitual = {True}"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()


def getSpellbook(discordId, charName):
    currentChar = getPlayerCharacters(discordId, True)
    if not currentChar:
        raise error.NoActiveCharacter()
    targetChar = getCharacter(charName)
    if not targetChar:
        raise error.UnknownCharacter()
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"SELECT s.name FROM spell s JOIN player_spell ps ON ps.spell = s.id JOIN player p ON ps.player = p.id WHERE s.isValid = 1 AND LOWER(p.char_name) = LOWER('{targetChar[0][1]}')"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()


def addSpellsToPlayer(discordId, spellListIds):
    db = connectDatabase()
    cursor = db.cursor()
    player = getPlayerCharacters(1)
    if player is not None:
        try:
            query = f"INSERT INTO player_spell VALUES(NULL, {discordId}, ?)"
            cursor.executemany(query, spellListIds)
            db.commit()
        finally:
            cursor.close()
            db.close()


def removeSpellsFromPlayer(discordId, spellListIds):
    db = connectDatabase()
    cursor = db.cursor()
    player = getPlayerCharacters(discordId)
    if player is not None:
        try:
            query = f"DELETE FROM player_spell WHERE LOWER(player) = LOWER({player[1]}) AND LOWER(spell) = LOWER(?)"
            cursor.executemany(query, spellListIds)
            db.commit()
        finally:
            cursor.close()
            db.close()


def findSpellByName(spellName):
    db = connectDatabase()
    cursor = db.cursor()
    try:
        query = f"SELECT * FROM spell WHERE LOWER(name) = LOWER('{spellName}') AND isValid = {True}"
        cursor.execute(query)
        spell = cursor.fetchone()
        if spell is not None:
            return spell
    finally:
        cursor.close()
        db.close()


def getPlayersWithSpell(spellName):
    spell = findSpellByName(spellName)
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"SELECT p.discord_id, p.char_name FROM player p JOIN player_spell ps ON ps.player = p.id WHERE LOWER(ps.spell) = LOWER('{spell[0]}')"
        cursor.execute(query)
        wizardList = cursor.fetchall()
        return wizardList
    except:
        print(f"There was an error trying to obtain the Wizard List")
    finally:
        cursor.close()
        db.close()


def getSubclass(subclass):
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"SELECT * FROM subclass s WHERE LOWER(s.subclass) = LOWER('{subclass}') AND s.isValid = {True}"
        cursor.execute(query)
        return cursor.fetchone()
    finally:
        cursor.close()
        db.close()


def getCharacter(charName):
    try:
        db = connectDatabase()
        cursor = db.cursor()
        query = f"SELECT p.discord_id, p.char_name, sc.subclass, p.wizard_level FROM player p JOIN subclass sc ON p.wizard_subclass = sc.id WHERE LOWER(p.char_name) = LOWER('{charName}') AND p.isActive = {True}"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()
