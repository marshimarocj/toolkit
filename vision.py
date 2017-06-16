from multiprocessing import Pool
import subprocess
import json

import cv2
import numpy as np
# from PIL mport Image
# from images2gif import writeGif

def isValidImg(imgFile, check_erode=True):
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

  if check_erode:
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


# def packImgFiles2Gif(imgFiles, outFile, duration, 
#     maxHeight=-1, compress=True):
#   imgs = []
#   for imgFile in imgFiles:
#     img = Image.open(imgFile)
#     width, height = img.size
#     if maxHeight != -1:
#       scale = maxHeight / float(height)
#       maxWidth = int(width*scale)
#       size = (maxWidth, maxHeight)
#       img.thumbnail(size)
#     imgs.append(img)
#   writeGif(outFile, imgs, duration=duration, dither=0)

#   if compress:
#     binary = [
#       'convert', outFile, 
#       '-coalesce', '-layers', 'OptimizeFrame', 
#       outFile]
#     cmd = ' '.join(binary)
#     proc = subprocess.Popen(cmd, shell=True)

#     proc.wait()


# def packImgs2Gif(imgs, outFile, duration, 
#     maxHeight=-1, compress=True):
#   _imgs = []
#   for img in imgs:
#     width, height = img.size
#     if maxHeight != -1:
#       scale = maxHeight / float(height)
#       maxWidth = int(width*scale)
#       size = (maxWidth, maxHeight)
#       img.thumbnail(size)
#     _imgs.append(img)
#   writeGif(outFile, _imgs, duration=duration, dither=0)

#   if compress:
#     binary = [
#       'convert', outFile, 
#       '-coalesce', '-layers', 'OptimizeFrame', 
#       outFile]
#     cmd = ' '.join(binary)
#     proc = subprocess.Popen(cmd, shell=True)

#     proc.wait()
