from sys import argv
import cv2
import time
import os
from tempfile import mkdtemp
import numpy as np
from skimage.metrics import structural_similarity as ssim
from glob import glob
import img2pdf
import subprocess
from tqdm import tqdm

def get_basic(img):
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  img = cv2.resize(img, (0, 0), fx=0.1, fy=0.1)
  return img
  
def deduplicate_images(tmpdir):
  frames = sorted(glob(f"{tmpdir}/*.jpg"))
  images = []
  for i in range(len(frames)):
    img = cv2.imread(frames[i])
    images.append(img)

  dup = []
  for i in tqdm(range(len(images))):
    for j in range(i+1, len(images)):
      s = ssim(get_basic(images[i]), get_basic(images[j]))
      if s > 0.9:
        dup.append(j)

  for i in range(len(dup)):
    try:
      os.remove(frames[dup[i]])
    except:
      continue

def convert_to_pdf(video, tmpdir):
  frames = sorted(glob(f"{tmpdir}/*.jpg"))
  print(f"Writing: {frames}")
  with open("%s.pdf" % (video).split('.')[0], "wb") as f:
    f.write(img2pdf.convert(frames))
  
def split_video(video, tmpdir):

  interval = 20

  subprocess.run([
    'ffmpeg',
    '-i',
    video,
    '-vf',
    f'fps=1/{interval}',
    '-f',
    'image2',
    f'{tmpdir}/thumb-%04d.jpg'], shell=False)

def main(argv):
  video = argv[1]
  tmpdir = mkdtemp()
  split_video(video, tmpdir)
  deduplicate_images(tmpdir)
  convert_to_pdf(video, tmpdir)

if __name__ == '__main__':
  main(argv)
