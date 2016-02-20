import random
import cv2

class ReservoirSampling:
  def __init__(self, poolSize):
    self.k = poolSize
    self.pool = []
    self.n = 0

  def addData(self, d):
    if self.n < self.k:
      self.pool.append(d)
      self.n += 1
      return

    r = random.randint(0, self.n)
    if r < self.k:
      self.pool[r] = d
    self.n += 1


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


def isValidImg(imgFile):
  try:
    img = cv2.imread(thumbFile)
  except:
    return False
    
  h, w, c = img.shape
  if h < 5 or w < 5: return False

  res = cv2.imresize(img, (128, 128))

  res = res.reshape((h*w, c))
  pixelStd = np.std(res, axis=1)
  pixelSum = np.sum(res, axis=1)
  stdIdx = set(np.nonzero(pixelStd == 0)[0])
  sumIdx = set(np.nonzero(pixelSum == 128*3)[0])
  erodeNum = len(stdIdx and sumIdx)

  if erodeNum >= 5000: return False

  return True