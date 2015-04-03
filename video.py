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
		if video_capturer == None:
			print("Error!")
		grab_status, grab_frame = video_capturer.read()
		Debug.Print("grab_status: %s" % str(grab_status))
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
		def __init__(self, v, start_frame=0):
			Debug.Print("__init__")
			assert start_frame < len(v) and start_frame >= 0,\
				"start_frame must be less than total frames."
			self.i = start_frame
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
			return (f,self.i-1)
		def __iter__(self):
			return self

	# start_frame should be 0-indexed
	def sub_iter(self, start_frame):
		Debug.Print("sub_iter")
		return Video.VideoIterator(self, start_frame)

	# These three methods will make Video act like an array.
	def __getitem__(self, index):
		if (type(index) == slice):
			# This is a slice operation.
			Debug.Print("__getitem__:slice")
			slice_video = Video(self.video_filename, self.grayscale)
			slice_video.video_frames = self.video_frames[index.start:index.stop]
			return slice_video
		else:
			Debug.Print("__getitem__")
			# This is a simple frame index operation.
			return self.video_frames[index]
	def __len__(self):
		Debug.Print("__len__")
		return len(self.video_frames)
	def __iter__(self):
		Debug.Print("__iter__")
		return Video.VideoIterator(self)

def TestVideo():
	#v = Video("centaur_1.mpg")
	v = Video("small.ogv")
	#v = Video("centaur_1.mpg", grayscale=True)
	v = Video("small.ogv", grayscale=True)
	sv = v[0:10]

	print("len(v): %d" % len(v))
	print("len(sv): %d" % len(sv))

	if not sv.dump_frames():
		print("Error occurred dumping frames.")

	print("for f,i in v:")
	for f,i in v:
		print("i,f: %d, %s" % (i, str(f)))

	print("for f,i in sv[5:]:")
	for f,i in sv[5:]:
		print("i,f: %d, %s" % (i, str(f)))

	print("for f,i in v.sub_iter(5):")
	for f,i in sv.sub_iter(5):
		print("i,f: %d, %s" % (i, str(f)))
if __name__== "__main__":
	TestVideo()
