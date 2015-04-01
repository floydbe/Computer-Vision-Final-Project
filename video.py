#!/usr/bin/env python

from __future__ import print_function
from debug import Debug
import cv2
import os
import os.path

class Video:
	def __init__(self, video_filename):
		self.video_filename = video_filename
		self.load()

	def load(self):
		self.video_frames = []
		video_capturer = cv2.VideoCapture(self.video_filename)
		grab_status, grab_frame = video_capturer.read()
		while grab_status:
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
			cv2.imwrite("%s/frame_%d.%s" % (output_dir, i+1, output_extension), frame)
		return True

def TestVideo():
	v = Video("centaur_1.mpg")
	if not v.dump_frames():
		print("Error occurred dumping frames.")

if __name__== "__main__":
	TestVideo()
