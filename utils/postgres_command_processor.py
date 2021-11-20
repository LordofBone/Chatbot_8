import psycopg2


def command_processor(postgres_connection, commands, fetch_all=None, keep_alive=True):
    """Has some handy code in to handle SQL queries into the DB and to deal with errors. I got this from
    stackoverflow but I can't find the source now. It has been slightly modified for the purposes of this Chatbot """
    fetched = None

    try:
        cursor = postgres_connection.cursor()
        # create table one by one
        for command in commands:
            cursor.execute(command)

        if fetch_all is True:
            fetched = cursor.fetchall()
        elif fetch_all is False:
            fetched = cursor.fetchone()

        # close communication with the PostgreSQL database server
        cursor.close()
    except psycopg2.errors.ProgramLimitExceeded:
        # todo: there seems to be a char limit for unique indexes - need to find a way to md5 indexes, this is a
        #  workaround for now; to just skip too long sentences
        fetched = "string_too_long"
    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception(error)
    finally:
        if postgres_connection is not None:
            if not keep_alive:
                postgres_connection.close()

        return fetched
