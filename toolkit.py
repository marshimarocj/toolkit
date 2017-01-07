import sys
import os
import logging

from Queue import Queue
import threading


def printTimeLen(seconds):
  iseconds = int(seconds)
  hours = iseconds // 3600
  minutes = (iseconds - hours*3600) // 60

  return '%02d:%02d:%02d:%03f'%(hours, minutes, iseconds%60, seconds-iseconds)


# proved to be useless
# class Prefetcher(object):
#   # fn should be a producer function with parameter q
#   def __init__(self, fn, size):
#     self.q = Queue(size)

#     t = threading.Thread(target=fn, args=(self.q,))
#     t.daemon = True # so that it could be terminated by Ctrl+C
#     t.start()

#   def get(self):
#     return self.q.get()


def set_logger(name, log_path=None):
  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)

  console = logging.StreamHandler()
  console.setLevel(logging.INFO)
  console.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
  logger.addHandler(console)

  if log_path is not None:
    if os.path.exists(log_path):
      os.remove(log_path)

    logfile = logging.FileHandler(log_path)
    logfile.setLevel(logging.INFO)
    logfile.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger.addHandler(logfile)

  return logger


# WARN: only process the 'y' branch, does nothing for else
def dirInteractiveChecker(dir):
  if not os.path.exists(dir):
    print '%s: not exists!'%(dir)
    print 'would you like to create "%s"?(y/n)'%(dir)
    line = sys.stdin.readline()
    line = line.strip()

    if line == 'y':
      os.makedirs(dir)
