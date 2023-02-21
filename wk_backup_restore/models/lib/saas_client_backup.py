# curl -X POST -F 'master_pwd=abcd' -F 'name=xyz' -F 'backup_format=zip' -o /path/xyz.zip http://localhost:8069/web/database/backup
import requests
import argparse
import os
import datetime
import psycopg2
from urllib.parse import urlparse


def init_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mpswd', action='store',
                        help='Master password Odoo')
    parser.add_argument('--url', action='store',
                        help='saas client url')
    parser.add_argument('--dbname', action='store',
                        help='name of database to backup')
    parser.add_argument('--maindb', action='store',
                        help='name of main database')
    parser.add_argument('--dbuser', action='store',
                        help='username of main database')
    parser.add_argument('--dbpassword', action='store',
                        help='password of main database')
    parser.add_argument('--processid', action='store',
                        help='process id')
    parser.add_argument('--bkploc', action='store',
                        help='backup location local, dedicated, s3')
    parser.add_argument('--path', action='store',
                        help='Master password Odoo')

    return parser.parse_args()


def database_entry(main_db, db_user, db_password, db_name, file_name, process_id, file_path, url, backup_date_time, status, message):
    try:
        if db_user == "False" or db_password == "False":
            connection = psycopg2.connect(database=main_db)
        else:
            connection = psycopg2.connect(user=db_user, password=db_password, host="127.0.0.1", port="5432", database=main_db)
    except Exception as e:
        print(e)
        print('Exited')
        exit(0)

    try:
        file_path = file_path.replace('//', '/')
        url = url.replace('//', '/')
        # Connect to database
        QUERY = "INSERT INTO backup_process_detail (name, file_name, backup_process_id, file_path, url, backup_date_time, status, message) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        RECORD = (db_name, file_name, process_id, file_path, url, backup_date_time, status, message)
        cursor = connection.cursor()
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        cursor.execute(QUERY, RECORD)
        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted")
    except Exception as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Postgresql Connection Closed")


def backup_db():
    print(args)
    data = {
        'master_pwd': args.mpswd,
        'name': args.dbname,
        'backup_format': 'zip'
    }

    client_url = ''
    msg = ''
    # print(urlparse(args.url).scheme=='')
    if urlparse(args.url).scheme == '':
        client_url = 'http://' + args.url + \
            ('/' if args.url[-1] != '/' else '')
    else:
        client_url = args.url + ('/' if args.url[-1] != '/' else '')

    if not os.path.exists(args.path):
        os.mkdir(args.path)

    
    backup_dir = os.path.join(args.path, 'backups')
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

    client_url += 'web/database/backup'
    # Without Streaming method
    print(client_url)
    #response = requests.post(client_url, data=data)
    # Streaming zip, so that everything is not stored in RAM.
    try:
        filename = args.dbname + '-' + datetime.datetime.now().strftime("%m-%d-%Y-%H") + '.zip'
        backed_up_file_path = os.path.join(backup_dir, filename)
        print(backed_up_file_path)
        with requests.post(client_url, data=data, stream=True) as response:
            response.raise_for_status()
            with open(os.path.join(backup_dir, filename), 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
        msg = 'Database backup Successful at ' + datetime.datetime.now().strftime("%m-%d-%Y-%H:%M:%S")
        database_entry(args.maindb, args.dbuser, args.dbpassword, args.dbname, filename, args.processid, backup_dir+'/', backed_up_file_path, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status="Success", message=msg)
        return {
            'success': True,
            'msg': msg
        }
    except Exception as e:
        msg = 'Failed at ' + datetime.datetime.now().strftime("%m-%d-%Y-%H:%M:%S") + ' ' + str(e)
        database_entry(args.maindb, args.dbuser, args.dbpassword, args.dbname, filename, args.processid, backup_dir+'/', backed_up_file_path, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status="Failure", message=msg)
        return {
            'success': False,
            'msg': msg
        }

if __name__ == '__main__':
    args = init_parser()
    print(backup_db())
    # database_entry("postgres", "postgres", "postgres", 'test_db', os.getcwd(), os.getpid(), os.getcwd(), '', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


