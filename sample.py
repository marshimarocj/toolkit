import random
import bisect

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
