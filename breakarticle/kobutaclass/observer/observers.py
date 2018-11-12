from breakarticle.model import db
from breakarticle.model.svs import Devices
from breakarticle.kobutaclass.observer import Observer
from breakarticle.kobutaclass.scheduler import Scheduler
import logging


from breakarticle.exceptions import AtomException


class DeviceFinishBaselineUploadObserver(Observer):

    def __init__(self, hash_id=None):
        super(DeviceFinishBaselineUploadObserver, self).__init__()

    def notify(self, *args, **kwargs):
        super(DeviceFinishBaselineUploadObserver, self).notify()


class SchedulerObserver(Observer, Scheduler):

    def __init__(self, hash_id):
        Scheduler.__init__(self, hash_id)

    def notify(self, *args, **kwargs):
        super(SchedulerObserver, self).notify()
        self.create_or_enable_schedule()
