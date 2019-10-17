import logging

def init_log(level=logging.INFO):
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level=level, format=log_format)
    return logging
