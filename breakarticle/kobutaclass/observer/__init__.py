import logging

class Observer(object):
    """
    Base observer class
    """
    def __init__(self):
        pass

    def register(self, observable=None):
        observable.register_observer(self)

    def notify(self, *args, **kwargs):
        logging.warn("{} is notified".format(self.__class__.__name__))
        # Should be override by children class