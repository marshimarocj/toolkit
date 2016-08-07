import sys
import os
import logging
from multiprocessing import Pool
import subprocess
from Queue import Queue
import threading

import random
import json
import bisect

import cv2
import numpy as np
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from PIL import Image
from images2gif import writeGif

  ####     ##    #    #  #####   #       ######
 #        #  #   ##  ##  #    #  #       #
  ####   #    #  # ## #  #    #  #       #####
      #  ######  #    #  #####   #       #
 #    #  #    #  #    #  #       #       #
  ####   #    #  #    #  #       ######  ######

class ReservoirSampling:

  def __init__(self, poolSize):

    self._k = poolSize
    self._pool = []
    self._n = 0

  def addData(self, d):

    if self._n < self._k:
      self._pool.append(d)
      self._n += 1
    else:
      r = random.randint(0, self._n)
      if r < self._k:
        self._pool[r] = d
      self._n += 1

  @property
  def pool(self):

    return self._pool


def samplePairs(recordNum, sampleNum):

  pairMax = recordNum * (recordNum-1) / 2

  rands = set()
  while len(rands) < sampleNum:
    r = random.randint(0, pairMax-1)
    if r in rands: continue
    rands.add(r)

  cumSum = 0
  cumPos = []
  for i in range(recordNum):
    cumSum += recordNum-i-1
    cumPos.append(cumSum)

  randPairs = []
  for r in rands:
    row = bisect.bisect_left(cumPos, r)
    i = row
    j = r-cumPos[i-1]+i+1 if i > 0 else r+i+1
    randPairs.append((i, j))

  return randPairs


  ####   #    #
 #    #  #    #
 #       #    #
 #       #    #
 #    #   #  #
  ####     ##

def isValidImg(imgFile):

  try:
    if type(imgFile) is str:
      img = cv2.imread(imgFile)
    else:
      img = cv2.imdecode(imgFile, cv2.CV_LOAD_IMAGE_COLOR)
  except:
    return False
    
  if img is None: return False
  
  h, w, c = img.shape
  if h < 5 or w < 5: return False

  res = cv2.resize(img, (128, 128))

  res = res.reshape((128*128, c))
  pixelStd = np.std(res, axis=1)
  pixelSum = np.sum(res, axis=1)
  stdIdx = set(np.nonzero(pixelStd == 0)[0])
  sumIdx = set(np.nonzero(pixelSum == 128*3)[0])
  erodeNum = len(stdIdx and sumIdx)

  # TODO: It's better to be substituted by fraction later
  if erodeNum >= 5000: return False

  return True


def isBlack(imgFile):

  img = cv2.imread(imgFile)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  blackNum = np.sum(gray < 25)
  totalNum = gray.shape[0] * gray.shape[1]
  # print blackNum / float(totalNum)
  if totalNum * 0.5 < blackNum:
    return True
  else:
    return False


def skipFrame(cap, n):

  while n > 0:
    cap.grab()
    n -= 1

  return cap


def _convertFormat(input):

  file = input[0]
  outFile = input[1]

  binary = [
    'ffmpeg',
    '-i', file,
    outFile
  ]
  cmd = ' '.join(binary)
  proc = subprocess.Popen(cmd, shell=True)

  return proc.wait()


def convertFormat(files, ofiles, processNum=8):

  p = Pool(processNum)
  inputs = zip(files, ofiles)
  p.map(_convertFormat, inputs)


def _shotDetect(input):

  file = input[0]
  outFile = input[1]
  threshold = input[2]

  custom = '"movie=%s,select=gt(scene\,%f)"'

  binary = [
    'ffprobe',
    '-v', 'quiet',
    '-show_frames',
    '-print_format', 'json=c=1',
    '-f', 'lavfi',
    custom%(file, outFile),
  ]
  cmd = ' '.join(binary + [custom%(file, threshold)])
  proc = subprocess.Popen(cmd, shell=True, stdout=open(outFile, 'w'))

  return proc.wait()


def shotDetect(files, ofiles, threshold=0.3, processNum=8):

  p = Pool(processNum)
  inputs = []
  for f in range(len(files)):
    inputs.append([files[f], ofiles[f], threshold])
  p.map(_shotDetect, inputs)


def _keyFrame(input):

  file = input[0]
  outFile = input[1]

  binary = [
    'ffprobe',
    '-v', 'quiet',
    '-show_frames',
    '-select_streams', 'v',
    '-print_format', 'json=c=1',
    '-show_entries', 'frame=pict_type',
  ]
  cmd = ' '.join(binary + [file])
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
  result = p.communicate()[0]

  data = json.loads(result)
  data = data['frames']
  keyFrameNums = []
  for i, d in enumerate(data):
    if d['pict_type'] == 'I':
      keyFrameNums.append(i)

  json.dump(keyFrameNums, open(outFile, 'w'))

  if len(input) == 3:
    outPrefix = input[2]
    cap = cv2.VideoCapture(file)
    for i in range(1, len(ke11yFrameNums)):
      gap = keyFrameNums[i] - keyFrameNums[i-1]
      skip(cap, gap)
      flag, img = cap.retrieve()
      outFile = '%s-%d.jpg'%(outPrefix, keyFrameNums[i])
      cv2.imwrite(outFile, img)

  return 0


def keyFrame(files, ofiles, processNum=8):

  p = Pool(processNum)
  p.map(_keyFrame, zip(files, ofiles))


def packImgs2Gif(imgFiles, outFile, duration, 
    maxHeight=-1, compress=True):
  imgs = []
  for imgFile in imgFiles:
    img = Image.open(imgFile)
    width, height = img.size
    if maxHeight != -1:
      scale = maxHeight / float(height)
      maxWidth = int(width*scale)
      size = (maxWidth, maxHeight)
      img.thumbnail(size)
    imgs.append(img)
  writeGif(outFile, imgs, duration=duration, dither=0)

  if compress:
    binary = [
      'convert', outFile, 
      '-coalesce', '-layers', 'OptimizeFrame', 
      outFile]
    cmd = ' '.join(binary)
    proc = subprocess.Popen(cmd, shell=True)

    proc.wait()


 #    #   #####     #    #
 #    #     #       #    #
 #    #     #       #    #
 #    #     #       #    #
 #    #     #       #    #
  ####      #       #    ######

def printTimeLen(seconds):

  iseconds = int(seconds)
  hours = iseconds // 3600
  minutes = (iseconds - hours*3600) // 60

  return '%02d:%02d:%02d:%03f'%(hours, minutes, iseconds%60, seconds-iseconds)


class Prefetcher(object):
  q = None

  # fn should be a producer function with parameter q
  def __init__(self, fn, size):

    self.q = Queue(size)

    t = threading.Thread(target=fn, args=(self.q,))
    t.daemon = True # so that it could be Ctrl+C
    t.start()

  def get(self):

    return self.q.get()


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


class ScpHelper(object):
  ssh = None
  scp = None

  def connect(self, key_file, dest, port, username):
    self.ssh = SSHClient()
    # paramiko.util.log_to_file("/tmp/tmp.log")
    k = paramiko.RSAKey.from_private_key_file(key_file)
    self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh.connect(dest, port=port, username=username, pkey=k)

    self.scp = SCPClient(self.ssh.get_transport())

  def shortcut(self, name):
    path = os.getenv("HOME")
    key_file = os.path.join(path, 'credential', name)
    dest = ''
    port = 22
    username = ''
    if name == 'sun':
      dest = '202.112.113.219'
      username = 'qjin'
    elif name == 'mercurial':
      dest = '202.112.113.209'
      username = 'chenjia'
    elif name == 'jupiter':
      dest = '222.29.195.82'
      port = 222
      username = 'qjin'
    elif name == 'earth':
      dest = '222.29.193.172'
      port = 226
      username = 'chenjia'
    elif name == 'rocks':
      dest = 'rocks.is.cs.cmu.edu'
      username = 'jiac'
    elif name == 'aladdin1':
      dest = 'aladdin1.inf.cs.cmu.edu'
      username = 'jiac'
    elif name == 'yy':
      dest = 'vid-gpu1.inf.cs.cmu.edu'
      username = 'jiac'
    elif name == 'xcl':
      dest = '128.2.219.108'
      username = 'informedia'

    return key_file, dest, port, username

  def get(self, remote_file, local_file, recursive=False):
    self.scp.get(remote_file, local_file, recursive=recursive)

  def put(self, local_files, remote_path, recursive=False):
    self.scp.put(local_files, remote_path, recursive=recursive)

  def disconnect(self):
    self.scp.close()


 #####    ####
 #    #  #
 #    #   ####
 #    #       #
 #    #  #    #
 #####    ####
 
class DisjointSet:

  class Node:

    _rank = -1
    _val = None
    _parent = None


    def __init__(self, val):

      self._rank = 1
      self._val = val
      self._parent = self


    @property
    def val(self):

      return self.val


  _sets = {}


  def __init__(self):

    self._sets = {}


  def makeSet(self, val):

    if val not in self._sets:
      self._sets[val] = self.Node(val)


  def join(self, valLhs, valRhs):

    lhs = self._sets[valLhs]
    rhs = self._sets[valRhs]
    lhsParent = self.find(lhs)
    rhsParent = self.find(rhs)

    if lhsParent == rhsParent:
      return

    parent = lhsParent
    child = rhsParent
    if lhsParent._rank < rhsParent._rank: # path compress
      parent = rhsParent
      child = lhsParent
    child._parent = parent
    parent._rank = max(parent._rank, child._rank+1)


  def find(self, node):

    nodes = [node]
    while node._parent != node:
      nodes.append(node)
      node = node._parent

    # path compress trick
    for i in range(1, len(nodes)):
      nodes[-i]._parent = nodes[-i+1]._parent

    return nodes[0]._parent

  def findVal(self, val):

    return self.find(self._sets[val])


  ####    #   #   ####
 #         # #   #
  ####      #     ####
      #     #         #
 #    #     #    #    #
  ####      #     ####

# WARN: only process the 'y' branch, does nothing for else
def dirInteractiveChecker(dir):

  if not os.path.exists(dir):
    print '%s: not exists!'%(dir)
    print 'would you like to create "%s"?(y/n)'%(dir)
    line = sys.stdin.readline()
    line = line.strip()

    if line == 'y':
      os.makedirs(dir)
