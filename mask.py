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

	def decide(self, frame, index, existing):
		return existing

class MedianMask(Mask):
	def __init__(self, video):
		super(MedianMask, self).__init__()
		self.video = video
		self._calculate_median()
	
	def threshold(self):
		return 0.05

	def decide(self, frame, index, existing):
		if abs(existing - self.mask[index[0]][index[1]]) < self.threshold():
			return 0.0
		else:
			return existing

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

class MedianMaskBackground(MedianMask):
	def __init__(self, video, background):
		super(MedianMaskBackground, self).__init__(video)
		self.background = background

	def decide(self, frame, index, existing):
		if abs(self.video[frame][index[0]][index[1]] -
			self.mask[index[0]][index[1]]) < self.threshold():
			return self.background[index[0], index[1]]
		else:
			return existing

class MedianMaskColorize(MedianMask):
	def __init__(self, video):
		super(MedianMaskColorize, self).__init__(video)
		self.rgb_gray_video = GrayVideo(video)
		for f,i in self.rgb_gray_video:
			self.rgb_gray_video[i] = skimage.img_as_ubyte(skimage.color.gray2rgb(f))

	def decide(self, frame, index, existing):
		if abs(self.video[frame][index[0]][index[1]] -
			self.mask[index[0]][index[1]]) < self.threshold():
			return self.rgb_gray_video[frame][index[0], index[1]]
		else:
			return existing

class MeanMask(Mask):
	def __init__(self, video):
		super(MeanMask, self).__init__()
		self.video = video
		self._calculate_mean()

	def threshold(self):
		return 0.10

	def decide(self, frame, index, existing):
		if abs(existing - self.mean[index[0]][index[1]]) < self.threshold():
			return 0.0
		else:
			return existing

	def _calculate_mean(self):
		mean_height = self.video[0].shape[0]
		mean_width = self.video[0].shape[1]
		meanl = [[ 0.0 \
			for x in range(mean_height) ]
			for x in range(mean_width) ]
		self.mask = [[ 0 \
			for x in range(mean_height) ]
			for x in range(mean_width) ]
		for f, i in self.video:
			for y in range(f.shape[0]):
				for x in range(f.shape[1]):
					meanl[y][x] += f[y][x]
		for y in range(mean_height):
			for x in range(mean_width):
				self.mask[y][x] = meanl[y][x] / len(self.video)

if __name__== "__main__":
	v = GrayVideo("test_inputs/small_sample2.ogv")
	v = v[72:82]
	m = MedianMask(v)
	v.apply_mask(m).to_animated_gif("median_gif.gif")
	m = MeanMask(v)
	v.apply_mask(m).to_animated_gif("mean_gif.gif")
	pass
