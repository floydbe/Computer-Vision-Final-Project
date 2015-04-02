#!/usr/bin/env python

from __future__ import print_function
from debug import Debug
import cv2
import os
import os.path
import skimage
import skimage.color
import skimage.io

class Video:
	def __init__(self, video_filename, grayscale=False):
		self.video_filename = video_filename
		self.grayscale = grayscale
		self.load()

	def load(self):
		self.video_frames = []
		video_capturer = cv2.VideoCapture(self.video_filename)
		grab_status, grab_frame = video_capturer.read()
		while grab_status:
			if self.grayscale:
				self.video_frames.append(skimage.color.rgb2gray(grab_frame))
			else:
				self.video_frames.append(grab_frame)
			grab_status, grab_frame = video_capturer.read()
		video_capturer.release()

	def dump_frames(self, output_dir="./frames", output_extension="jpg"):
		# Check if output_dir exists. Create it if
		# it does not.
		if not os.path.isdir(output_dir):
			try:
				os.mkdir(output_dir)
			except OSError as e:
				Debug.Print("Error: " + str(e))
				return False

		# Loop through frames and output them.
		for frame,i in zip(self.video_frames, range(len(self.video_frames))):
			#cv2.imwrite("%s/frame_%d.%s" % (output_dir, i+1, output_extension), frame)
			skimage.io.imsave("%s/frame_%d.%s" % (output_dir, i+1, output_extension), frame)
		return True

	class VideoIterator:
		def __init__(self, v):
			Debug.Print("__init__")
			self.i = 0
			self.v = v
		def __len__(self):
			Debug.Print("__len__")
			return len(self.v)
		def next(self):
			Debug.Print("next")
			if self.i >= len(self.v):
				raise StopIteration
			f = self.v[self.i]
			self.i = self.i + 1
			return f

	# These three methods will make Video act like an array.
	def __getitem__(self, index):
		Debug.Print("__getitem__")
		return self.video_frames[index]
	def __len__(self):
		Debug.Print("__len__")
		return len(self.video_frames)
	def __iter__(self):
		Debug.Print("__iter__")
		return Video.VideoIterator(self)

def TestVideo():
	v = Video("centaur_1.mpg")
	#v = Video("centaur_1.mpg", grayscale=True)
	if not v.dump_frames():
		print("Error occurred dumping frames.")
	print("len(v): %d" % len(v))
	#for i in range(len(v)):
	for f,i in zip(v, range(len(v))):
		print("i,f: %d, %s" % (i, str(f)))

if __name__== "__main__":
	TestVideo()
