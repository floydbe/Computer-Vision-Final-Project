#!/usr/bin/env python

import cv2
import numpy as np
import Image
from video import Video
from distance import d

def Match():
	v = Video("centaur_1.mpg", grayscale=True)

	for f,i in v:
		print("i: %d" % i)
		for g,j in v[i:]:
			print("d(%d,%d) = %f" % (i, i+j, 0.0))#d(f,g)))

if __name__== "__main__":
	Match()
