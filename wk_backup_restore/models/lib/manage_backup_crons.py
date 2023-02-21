from crontab import CronTab
import datetime
import logging
import getpass

PYTHON_ENV = "/usr/bin/python3"
LOG_FILE_PATH = "/var/log/odoo/backup_cron.log"
BACKUP_SCRIPT_PATH = "/odoo/webkul_addons/wk_backup_restore/models/lib/saas_client_backup.py"

_logger = logging.getLogger(__name__)

class Cronjob:
    def __init__(self, command, create_time, frequency, frequency_cycle):
        self.command = command
        self.create_time = create_time
        self.frequency = frequency
        self.frequency_cycle = frequency_cycle
        self.user = getpass.getuser()
        self.cron = CronTab(user=self.user)

    @staticmethod
    def create_command(masterpswd, url, main_db, db_name, db_user, db_password, process_id, backup_location, storage_path, module_path):
        return "{} {} --mpswd {} --url {} --dbname {} --maindb {} --dbuser {} --dbpassword {} --processid {} --bkploc {} --path {} >> {} 2>&1".format(PYTHON_ENV, module_path, masterpswd, url, db_name, main_db, db_user, db_password, process_id, backup_location, storage_path, LOG_FILE_PATH)

    def set_time_for_cron(self):
        _logger.info(self.frequency_cycle)
        self.job.minute.on(0)
        date, time = self.create_time.split(',')
        m, d, y = map(int, date.split('/'))
        h, mi, s = map(int, time.split(':'))
        if self.frequency_cycle == 'half_day':
            h%=12
            self.job.hour.during(h, 23).every(12)
            self.job.minute.on(mi)
            self.job.dow.on()
            self.job.dom.on()
            return True
        elif self.frequency_cycle == 'daily':
            if self.frequency == 1:
                self.job.hour.on(h)
                self.job.minute.on(0)
                self.job.dow.on()
                self.job.dom.on()
                return True
            else:
                return False
        elif self.frequency_cycle == 'weekly' or self.frequency_cycle == 'week':
            # datetime.datetime(self.create_time)
            _logger.info("time %r" %h)
            day_of_week = datetime.datetime(y,m,d).weekday() + 1
            if self.frequency == 1:
                self.job.dow.on(day_of_week)
                self.job.hour.on(h)
                self.job.minute.on(0)
                self.job.day.on()
                # print('kkkkkk', self.job)
                return True
            else:
                return False
        elif self.frequency_cycle == 'monthly' or self.frequency_cycle == 'month':
            if self.frequency == 1:
                self.job.dom.on(d)
                self.job.hour.on(h)
                self.job.minute.on(mi)
                # self.job.dow.on()
                # self.job.every(d).dom()
                return True
            else:
                return False
        elif self.frequency_cycle == 'yearly' or self.frequency_cycle == 'year':
            if self.frequency == 1:
                self.job.dom.on(d)
                self.job.hour.on(h)
                self.job.minute.on(mi)
                self.job.month.on(m)
                # self.job.dow.on()
                # self.job.every(d).dom()
                return True
            else:
                return False
        

    def create_cronjob(self):
        job = self.cron.new(
            command=self.command)
        self.job = job
        self.set_time_for_cron()
        return True

    def write_crontab(self):
        try:
            self.cron.write()
            return {
                "success": True,
                "msg": None
            }
        except Exception as e:
            return {
                "success": False,
                "msg": str(e)
            }

    def remove_cron(self):
        job = list(self.list_cronjobs(self.command))
        _logger.info("%s"%(job[0]))
        if len(job) == 1:
            self.cron.remove(job[0])

    def list_cronjobs(self, search_keyword=None):
        if search_keyword:
            return self.cron.find_command(search_keyword)
        return self.cron.lines

    def update_cronjob(self):
        _logger.info("Updating Job")
        jobs = list(self.list_cronjobs(self.command))
        _logger.info("%s"%(jobs[0]))
        if len(jobs) == 1:
            self.job = jobs[0]
            res = self.set_time_for_cron()
            if res:
                return {
                        'success': True,
                        'msg': self.job
                        }
            else:
                return {
                        'success': False,
                        'msg': 'Invalid Time.'
                        }
        else:
            # More than one cron for same client.
            return self.jobs


    # set_cron_for_new_client(masterpwd, url, dbname, backup_location, interval, create_time, storage_path, cycle)
def add_cron(master_pass, url, main_db, db_name, db_user, db_password, process_id, backup_location, frequency, frequency_cycle, storage_path, module_path):
    _logger.info(locals())
    command = Cronjob.create_command(master_pass, url, main_db, db_name, db_user, db_password, process_id, backup_location, storage_path, module_path)
    _logger.info("%s"%(command))
    create_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    #create_time = "16:00"
    cj = Cronjob(command, create_time, frequency, frequency_cycle)
    cj.create_cronjob()
    wc = cj.write_crontab()
    if wc['success']:
        _logger.info("Added Job Successfully")
    else:   
        _logger.info("ERROR: %s"%(wc['msg']))

    return wc

def update_cron(db_name, frequency, frequency_cycle):
    command = db_name
    create_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    cj = Cronjob(command, create_time, frequency, frequency_cycle)
    uc = cj.update_cronjob()
    if uc['success'] == False:
        return uc
    else:
        wc = cj.write_crontab()
        if wc['success']:
            _logger.info("Updated Job Successfully")
        else:
            _logger.info("ERROR: %s"%(wc['msg']))

        return wc

def remove_cron(db_name, frequency, frequency_cycle):
    command = db_name
    create_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    cj = Cronjob(command, create_time, frequency, frequency_cycle)
    cj.remove_cron()
    wc = cj.write_crontab()
    if wc['success']:
        _logger.info("Removed Job Successfully")
    else:
        _logger.info("ERROR: %s"%(wc['msg']))

    return wc

if __name__ == '__main__':
    import os
    master_pass = 'CnvvV46UGZb2=N'
    url = 'http://192.168.5.125/'
    main_db = 'postgres'
    db_name = 'test_backup_crone.odoo-saas.webkul.com'
    db_user = 'postgres'
    db_password = 'postgres'
    process_id = 1234
    backup_location = 'local'
    frequency_cycle = 'weekly' # monthly, weekly, yearly, half_day.
    frequency = 2 if frequency_cycle == 'half_day' else 1
    module_path = '/opt/webkul_addons/wk_backup_restore/models/lib/saas_client_backup.py'
    storage_path = os.getcwd()
    update_cron(db_name, frequency, frequency_cycle)
    # add_cron(master_pass, url, main_db, db_name, db_user, db_password, process_id, backup_location, frequency, frequency_cycle, storage_path, module_path)
    _logger.info(update_cron(db_name, frequency, frequency_cycle))
