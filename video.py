#!/usr/bin/env python

from __future__ import print_function
from debug import Debug
import cv2
import os
import os.path
import skimage
import skimage.color
import skimage.io
import skimage.filter
import skimage.transform
import shutil
import make_gif
import tempfile

class Video(object):
	def __init__(self, video, grayscale=False):
		if isinstance(video,Video):
			self.video_filename = video.video_filename
			self.grayscale = video.grayscale
			self.video_frames = video.video_frames
			self.frames_per_second = video.frames_per_second
		else:
			self.video_filename = video
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
			grab_frame = cv2.cvtColor(grab_frame, cv2.COLOR_BGR2RGB)
			if self.grayscale:
				self.video_frames.append(skimage.color.rgb2gray(grab_frame))
			else:
				self.video_frames.append(grab_frame)
			grab_status, grab_frame = video_capturer.read()

		# Determine the FPS
		# This must be done at the end of the loop so that we are getting
		# accurate information about the actual number of total frames
		# in the video but especially about the total playback time.
		#
		frame_count = video_capturer.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
		video_length = video_capturer.get(cv2.cv.CV_CAP_PROP_POS_MSEC)/1000.0
		self.frames_per_second = int(frame_count/video_length)

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
			skimage.io.imsave("%s/frame_%04d.%s" % (output_dir, i+1, output_extension), frame)
		return True

	def to_animated_gif(self, gif_name):
		temp_folder_name = tempfile.mkdtemp()
		self.dump_frames(temp_folder_name, "jpg")
		make_gif.make_gif(temp_folder_name, frames_per_sec=self.frames_per_second, output_file_loc=gif_name)
		# Not wild about using this helper.
		shutil.rmtree(temp_folder_name, ignore_errors=True)

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

class EdgeVideo(Video):
	def __init__(self, parameter, grayscale=False):
		if isinstance(parameter,Video):
			Debug.Print("Converting from Existing Video (parameter is video).")
		else:
			Debug.Print("New Video entirely (parameter is filename).")
		super(self.__class__, self).__init__(parameter, grayscale)
		#
		# Now, let's edgify each frame.
		#
		if not type(parameter) == EdgeVideo:
			Debug.Print("Canny-fying.")
			new_video_frames = []
			for f in self.video_frames:
				new_video_frames.append(skimage.img_as_float(skimage.filter.canny(f)))
			self.video_frames = new_video_frames
			Debug.Print("len(new_video_frames): %d" % len(new_video_frames))
		pass
class ScaleVideo(Video):
	def __init__(self, parameter, grayscale=False):
		if isinstance(parameter,Video):
			Debug.Print("Converting from Existing Video (parameter is video).")
		else:
			Debug.Print("New Video entirely (parameter is filename).")
		super(self.__class__, self).__init__(parameter, grayscale)
		#
		# Now, let's scale each frame as long as
		# this isn't already a scaled video.
		#
		if not type(parameter) == ScaleVideo:
			Debug.Print("Scaling.")
			new_video_frames = []
			for f in self.video_frames:
				new_f = skimage.transform.resize(f,(128,128))
				new_video_frames.append(new_f)
			self.video_frames = new_video_frames
			Debug.Print("len(new_video_frames): %d" % len(new_video_frames))
		pass

def TestVideo():
	#v = Video("centaur_1.mpg")
	print("v = Video(\"small.ogv\")")
	v = Video("small.ogv")
	print("ev = EdgeVideo(\"small.ogv\", grayscale=True)")
	ev = EdgeVideo("small.ogv", grayscale=True)
	print("ev = EdgeVideo(ev)")
	ev = EdgeVideo(ev)
	print("sv = v[0:10]")
	sv = v[0:10]
	print("scalev = ScaleVideo(v)")
	scalev = ScaleVideo(v)
	print("scalev = ScaleVideo(\"small.ogv\")")
	scalev = ScaleVideo("small.ogv")

	print("len(v): %d" % len(v))
	print("len(sv): %d" % len(sv))

	print("v.dump_frames()")
	if not v.dump_frames():
		print("Error occurred dumping frames.")

	print("sv.to_animated_gif(\"output_gif.gif\")")
	ev.to_animated_gif("output_gif.gif")

	print("for f,i in v.sub_iter(5):")
	for f,i in sv.sub_iter(5):
		print("i: %d" % (i))
if __name__== "__main__":
	TestVideo()
