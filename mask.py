#!/usr/bin/env python

from __future__ import print_function
from debug import Debug
import cv2
import os
import os.path
from video import Video, GrayVideo
import skimage
import skimage.color
import skimage.io
import skimage.filter
import skimage.transform
import shutil
import make_gif
import tempfile
import numpy

class Mask(object):
	def __init__(self):
		self.mask = None

	def __getitem__(self, index):
		if self.mask and index<len(self.mask):
			return self.mask[index]
		return None
	
	def threshold(self):
		return 0.0

class MedianMask(Mask):
	def __init__(self, video):
		super(self.__class__, self).__init__()
		self.video = video
		self._calculate_median()
	
	def threshold(self):
		return 0.05

	def _calculate_median(self):
		median_height = self.video[0].shape[0]
		median_width = self.video[0].shape[1]
		medianl = [[ [] \
			for x in range(median_height) ]
			for x in range(median_width) ] 
		self.mask = [[ 0 \
			for x in range(median_height) ]
			for x in range(median_width) ] 
		for f, i in self.video:
			for y in range(f.shape[0]):
				for x in range(f.shape[1]):
					medianl[y][x].append(f[y][x])
		for y in range(median_height):
			for x in range(median_width):
				self.mask[y][x] = numpy.median(medianl[y][x])

if __name__== "__main__":
	v = GrayVideo("test_inputs/small_sample2.ogv")
	v = v[72:82]
	m = MedianMask(v)
	v.apply_mask(m).to_animated_gif("median_gif.gif")
	pass
