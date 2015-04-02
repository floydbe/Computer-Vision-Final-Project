#!/usr/bin/env python

import cv2
import numpy as np
import Image
from video import Video
from distance import d

def Match():
	v = Video("centaur_1.mpg", grayscale=True)

	for f,i in zip(v, range(len(v))):
		print("i: %d" % i)
		for g,j in zip(v.sub_iter(i), range(len(v))):
			print("d(%d,%d) = %f" % (i, i+j, d(f,g)))

if __name__== "__main__":
	Match()
