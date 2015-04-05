#!/usr/bin/env python

import cv2
import numpy as np
import Image
from video import Video, EdgeVideo
from distance import d
import sys
import getopt
import re
from debug import Debug
from operator import itemgetter

def Match(v, start_frame, end_frame):
	#ev = EdgeVideo(v)
	matches = []
	for f,i in v.sub_iter(start_frame):
		Debug.Print("i: %d" % i)
		if i > end_frame:
			break
		for g,j in v.sub_iter(i):
			Debug.Print("d(%d,%d) = %f" % (i, j, 0.0))
			matches.append((i,j,d(f,g)))
	return matches

def usage(myname):
	print("""%s 
	[-s, --start <start frame>]
	[-e, --end <end frame> ] 
	<video filename>""" % myname)

if __name__== "__main__":
	start_frame = 0
	end_frame = None
	video = None
	filename = None

	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:e:", ["start=", "end="])

		if len(args) != 1:
			raise getopt.GetoptError("Must specify a single filename as parameter.")
		filename = args[0]

		for o, a in opts:
			o = re.sub("^-*", "", o)
			if o == "s" or o == "start":
				start_frame = int(a)
			elif o == "e" or o == "end":
				end_frame = int(a)

			print("%s=%s" % (o,a))
	except getopt.GetoptError as error:
		usage(sys.argv[0])
		sys.exit(1)

	video = Video(filename, grayscale=True)
	if end_frame == None:
		end_frame = len(video)
	matches = Match(video, start_frame, end_frame)
	matches = sorted(matches, key=itemgetter(2))
	# print matches in csv style.
	for match in matches:
		print("%d,%d,%f" % (match[0], match[1], match[2]))
