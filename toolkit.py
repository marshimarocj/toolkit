import random
from multiprocessing import Pool
import subprocess

import cv2
import numpy as np

########sample########
class ReservoirSampling:
  def __init__(self, poolSize):
    self._k = poolSize
    self._pool = []
    self._n = 0

  def addData(self, d):
    if self._n < self._k:
      self._pool.append(d)
      self._n += 1
      return

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
  for i in range(phraseNum):
    cumSum += phraseNum-i-1
    cumPos.append(cumSum)

  randPairs = []
  for r in rands:
    row = bisect.bisect_left(cumPos, r)
    i = row
    j = r-cumPos[i-1]+i+1 if i > 0 else r+i+1
    randPairs.append((i, j))

  return randPairs


########cv########
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

  if erodeNum >= 5000: return False

  return True


def skipFrame(cap, n):
  while n > 0: 
    cap.grab()
    n -= 1

  return cap


def shotDetect(files, ofiles, threshold=0.3, processNum=8):
  def ffprobe(input):
    file = input[0]
    outFile = input[1]

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

  p = Pool(phraseNum)
  p.map(ffprobe, zip(files, ofiles))


def keyFrame(files, ofiles, processNum=8):
  def ffprobe(input):
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

    return 0

  p = Pool(processNum)
  p.map(ffprobe, zip(files, ofiles))


########utility########
def printTimeLen(seconds):
  seconds = int(seconds)
  hours = seconds // 3600
  minutes = (seconds - hours*3600) // 60
  print '%dh%dm%ds'%(hours, minutes, seconds%60)


########data structure########
class DisjointSet:
  class Node:
    def __init__(self, val):
      self._rank = 1
      self._val = val
      self._parent = self

    @property
    def val(self):
      return self.val

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
    if lhsParent._rank < rhsParent._rank:
      parent = rhsParent
      child = lhsParent
    child._parent = parent
    parent._rank = max(parent._rank, child._rank+1)

  def find(self, node):
    nodes = [node]
    while node._parent != node:
      nodes.append(node)
      node = node._parent
    for i in range(1, len(nodes)):
      nodes[-i]._parent = nodes[-i+1]._parent

    return nodes[0]._parent

  def findVal(self, val):
    return self.find(self._sets[val])