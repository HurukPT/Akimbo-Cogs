import math
import sqlite3
import os.path
from os.path import exists
#from . import customExceptions as error
import customExceptions as error

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
    try:
        level = int(level)
    except ValueError:
        raise error.InvalidCharacterLevel()
    if level < 1 or level > 20:
        raise error.InvalidCharacterLevel()
    db = connectDatabase()
    cursor = db.cursor()
    school = getSubclass(subclass)
    if not school:
        raise error.UnknownSubclass()
    currentChar = getPlayerCharacters(discordId, True)
    if currentChar:
        raise error.ActiveCharExists()
    try:
        query = f"INSERT INTO 'player' VALUES(NULL, '{discordId}', '{charName}', '{school[0][0]}', '{level}', 1)"
        cursor.execute(query)
        db.commit()
    finally:
        cursor.close()
        db.close()


def retireCharacter(discordId):
    currentChar = getPlayerCharacters(discordId, True)
    if not currentChar:
        raise error.NoActiveCharacter()
    db = connectDatabase()
    cursor = db.cursor()
    try:
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
    db = connectDatabase()
    cursor = db.cursor()
    try:
        query = f"UPDATE 'player' SET isActive = {True} WHERE discord_id = '{discordId}' AND char_name = '{charName}' AND isActive = {False}"
        cursor.execute(query)
        db.commit()
        return cursor.rowcount > 1
    finally:
        cursor.close()
        db.close()


def getPlayerCharacters(discordId, isActive=True):
    db = connectDatabase()
    cursor = db.cursor()
    try:
        query = f"SELECT * FROM 'player' WHERE player.discord_id = {discordId}"
        if isActive:
            query += f" AND player.isActive = {isActive}"
        cursor.execute(query)
        return cursor.fetchmany()
    except:
        print(f"Error while retrieving data for {discordId}")
    finally:
        cursor.close()
        db.close()


def setLevelForPlayer(discordId, level):
    if (level >= 0 and level <= 20):
        db = connectDatabase()
        cursor = db.cursor()
        player = getPlayerCharacters(discordId)
        if player is not None:
            try:
                query = f"UPDATE 'player' SET wizard_level = {level} WHERE discord_id = {discordId}"
                cursor.execute(query)
                db.commit()
                return True
            except:
                print(f"Error while updating the level for {player[2]}")
            finally:
                cursor.close()
                db.close()
    return False


def getSpellListForPlayer(discordId):
    db = connectDatabase()
    cursor = db.cursor()
    player = getPlayerCharacters(discordId)
    if player is not None:
        try:
            query = f"SELECT * FROM 'spell' where isValid = {True} AND level <= {math.ceil(player[4] / 2)} "
            if "Graviturgist" not in player:
                query = query + f"AND isDunamancy = {False}"
            cursor.execute(query)
            return cursor.fetchall()
        except:
            print(f"Error while fetching spells for {player[1]}")
        finally:
            cursor.close()
            db.close()
    else:
        print("Player does not exist")


def getSpellFromPlayer(discordId):
    db = connectDatabase()
    cursor = db.cursor()
    player = getPlayerCharacters(discordId)
    if player is not None:
        try:
            query = f"SELECT s.* FROM 'spell' s JOIN 'player_spell' ps ON ps.spell = s.id WHERE isValid = {True} AND ps.player = {player[1]}"
            cursor.execute(query)
            return cursor.fetchall()
        except:
            print(f"Error while fetching spells for {player[1]}")
        finally:
            cursor.close()
            db.close()
    else:
        print("Player does not exist")


def addSpellsToPlayer(discordId, spellListIds):
    db = connectDatabase()
    cursor = db.cursor()
    player = getPlayerCharacters(1)
    if player is not None:
        try:
            query = f"INSERT INTO 'player_spell' VALUES(NULL, {discordId}, ?)"
            cursor.executemany(query, spellListIds)
            db.commit()
        except:
            print(f"Error while inserting spells for {player[2]}")
        finally:
            cursor.close()
            db.close()


def removeSpellsFromPlayer(discordId, spellListIds):
    db = connectDatabase()
    cursor = db.cursor()
    player = getPlayerCharacters(discordId)
    if player is not None:
        try:
            query = f"DELETE FROM 'player_spell' WHERE player = {player[1]} AND spell = ?"
            cursor.executemany(query, spellListIds)
            db.commit()
        except:
            print(f"Error while removing spells for {player[2]}")
        finally:
            cursor.close()
            db.close()


def findSpellByName(spellName):
    db = connectDatabase()
    cursor = db.cursor()
    try:
        query = f"SELECT * FROM 'spell' WHERE LOWER(name) = LOWER('{spellName}') AND isValid = {True}"
        cursor.execute(query)
        spell = cursor.fetchone()
        if spell is not None:
            return spell
    except:
        print(f"Spell {spellName} does not exist")
    finally:
        cursor.close()
        db.close()


def getPlayersWithSpell(spellName):
    db = connectDatabase()
    cursor = db.cursor()
    spell = findSpellByName(spellName)
    try:
        query = f"SELECT p.discord_id, p.char_name FROM player p JOIN player_spell ps ON ps.player = p.id WHERE ps.spell = '{spell[0]}'"
        cursor.execute(query)
        wizardList = cursor.fetchmany()
        return wizardList
    except:
        print(f"There was an error trying to obtain the Wizard List")
    finally:
        cursor.close()
        db.close()


def getSubclass(subclass):
    db = connectDatabase()
    cursor = db.cursor()
    try:
        query = f"SELECT * FROM subclass s WHERE LOWER(s.subclass) = LOWER('{subclass}') AND s.isValid = {True}"
        cursor.execute(query)
        return cursor.fetchmany()
    finally:
        cursor.close()
        db.close()


unretireCharacter(155363631498919936, "Oonen Dwinanea")
