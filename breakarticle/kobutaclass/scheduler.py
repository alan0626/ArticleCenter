from breakarticle.model import db
from breakarticle.model.svs import Schedules as ScheduleModel
from breakarticle.exceptions import AtomBadRequestError
from celery.schedules import crontab_parser
import logging


class Scheduler():
    """
    TMIS schedule format :
    hourly => day_of_week: -1
              hour_of_day: -1
    daily =>  day_of_week: -1
              hour_of_day: 0 - 23
    weekly => day_of_week: 1 - 7 (Mon - Sun)
              hour_of_day: 0 - 23

    This class sets default schedule at daily 00:00 triggers svs scanning task
    """

    def __init__(self, hash_id,  day_of_week=-1, hour_of_day=0):
        self.hash_id = hash_id
        self.atom_day_of_week = day_of_week
        self.atom_hour_of_day = hour_of_day
        self._convert_to_crontab()

    def _convert_to_crontab(self):
        day_of_week = self.atom_day_of_week
        hour_of_day = self.atom_hour_of_day
        if day_of_week == -1 and hour_of_day == -1: # hourly
            logging.info('hourly because day_of_week=%s, hour_of_day=%s', day_of_week, hour_of_day)
            self._set_crontab_schedule(minute='0')
        elif day_of_week == -1 and 24 > hour_of_day > -1: # daily, default case
            logging.info('daily because day_of_week=%s, hour_of_day=%s', day_of_week, hour_of_day)
            self._set_crontab_schedule(minute='0', hour=str(hour_of_day))
        elif 8 > day_of_week > 0: # weekly
            logging.info('weekly because day_of_week=%s, hour_of_day=%s', day_of_week, hour_of_day)
            self._set_crontab_schedule(minute='0', hour='0', day_of_week=str(day_of_week % 7))
        else:
            raise AtomBadRequestError(message='day_of_week={}, hour_of_day={}'.format(day_of_week, hour_of_day))
        return self

    def _set_crontab_schedule(self, minute='*', hour='*', day_of_month='*', day_of_week='*', month_of_year='*'):
        self.minute = str(minute)
        self.hour = str(hour)
        self.day_of_month = str(day_of_month)
        self.day_of_week = str(day_of_week)
        self.month_of_year = str(month_of_year)

        self.minutes = crontab_parser(60).parse(self.minute)
        self.hours = crontab_parser(24).parse(self.hour)
        self.days_of_week = crontab_parser(7).parse(self.day_of_week)
        self.days_of_month = crontab_parser(31, 1).parse(self.day_of_month)
        self.months_of_year = crontab_parser(12, 1).parse(self.month_of_year)

    def get_schedule_dict(self):
        return dict(
            minute=self.minute,
            hour=self.hour,
            day_of_month=self.day_of_month,
            day_of_week=self.day_of_week,
            month_of_year=self.month_of_year
        )

    def create_or_enable_schedule(self, commit=True):
        schedule = ScheduleModel.query.filter_by(hash_id=self.hash_id).first()
        if schedule is None:
            schedule_dict = self.get_schedule_dict().copy()
            schedule_dict['hash_id'] = self.hash_id
            schedule = ScheduleModel(**schedule_dict)
            db.session.add(schedule)
        else:
            schedule.enable()
        if commit:
            db.session.commit()
        return schedule

def disable_schedule(hash_id):
    pass
