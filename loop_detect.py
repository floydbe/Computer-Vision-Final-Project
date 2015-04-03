#!/usr/bin/env python

import cv2
import numpy as np
import Image
from video import Video, EdgeVideo
from distance import d

def Match():
	v = Video("centaur_1.mpg", grayscale=True)
	ev = EdgeVideo(v)
	for f,i in ev:
		print("i: %d" % i)
		for g,j in v.sub_iter(i):
			print("d(%d,%d) = %f" % (i, j, d(f,g)))

if __name__== "__main__":
	Match()
