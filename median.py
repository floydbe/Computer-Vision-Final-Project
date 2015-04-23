#!/usr/bin/env python

from __future__ import print_function
from debug import Debug
import cv2
import os
import os.path
from video import Video
import skimage
import skimage.color
import skimage.io
import skimage.filter
import skimage.transform
import shutil
import make_gif
import tempfile
import numpy

class Median(object):
	def __init__(self, video):
		self.video = video
		self._median = None

	def median(self):
		if self._median == None:
			self._calculate_median()
		return self._median

	def _calculate_median(self):
		median_height = self.video[0].shape[0]
		median_width = self.video[0].shape[1]
		medianl = [[ [] \
			for x in range(median_height) ]
			for x in range(median_width) ] 
		self._median = [[ 0 \
			for x in range(median_height) ]
			for x in range(median_width) ] 
		for f, i in self.video:
			for y in range(f.shape[0]):
				for x in range(f.shape[1]):
					medianl[y][x].append(f[y][x])
		for y in range(median_height):
			for x in range(median_width):
				self._median[y][x] = numpy.median(medianl[y][x])

	def subtract_median(self):
		median = self.median()
		mvideo = Video(self.video)
		for f, i in mvideo:
			for y in range(f.shape[0]):
				for x in range(f.shape[1]):
					if abs(f[y][x] - median[y][x]) <= 0.05:
						f[y][x] = 0.0
			mvideo[i] = f
		return mvideo

if __name__== "__main__":
	v = Video("test_inputs/small_sample2.ogv", grayscale=True)
	v = v[72:82]
	m = Median(v)
	m.subtract_median().to_animated_gif("median_gif.gif")
	pass
