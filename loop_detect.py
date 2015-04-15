#!/usr/bin/env python

import cv2
import numpy as np
import Image
from video import Video, EdgeVideo, GrayVideo, ScaleVideo
from distance import d
import sys
import getopt
import re
from debug import Debug
from operator import itemgetter

def Match(v, start_frame, end_frame):
	matches = []
	for f,i in v.sub_iter(start_frame):
		Debug.Print("i: %d" % i)
		if i > end_frame:
			break
		for g,j in v.sub_iter(i):
			distance = 0.0
			if i != j:
				distance = d(f,g)
			matches.append((i,j,distance))
			Debug.Print("d(%d,%d) = %f" % (i, j, distance))
	return matches

def usage(myname):
	print("""%s 
	[-s, --start <start frame>]
	[-e, --end <end frame> ] 
	[-o, --optimize ]
	[-t, --threshold <threshold> (only applicable in combination with -o)]
	<video filename>""" % myname)

if __name__== "__main__":
	start_frame = 0
	end_frame = None
	video = None
	filename = None
	threshold = 0.20
	do_edge_match_optimization = False

	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:e:ot:", ["start=", "end=", "optimize", "threshold="])

		if len(args) != 1:
			raise getopt.GetoptError("Must specify a single filename as parameter.")
		filename = args[0]

		for o, a in opts:
			o = re.sub("^-*", "", o)
			if o == "s" or o == "start":
				start_frame = int(a)
			elif o == "e" or o == "end":
				end_frame = int(a)
			elif o == "o" or o == "optimize":
				do_edge_match_optimization = True
			elif o == "t" or o == "threshold":
				threshold = float(a)
			print("%s=%s" % (o,a))
	except getopt.GetoptError as error:
		usage(sys.argv[0])
		sys.exit(1)

	video = Video(filename)
	video = GrayVideo(video)
	if end_frame == None:
		end_frame = len(video)

	matches = []
	if do_edge_match_optimization:
		edge_video = EdgeVideo(video)
		edge_matches = Match(edge_video, start_frame, end_frame)
		edge_matches = sorted(edge_matches, key=itemgetter(2))
		# compute full matches for good edge matches
		for a,b,distance in edge_matches:
			if distance < threshold:
				matches.append((a,b,d(video[a],video[b])))
	else:
		matches = Match(video, start_frame, end_frame)

	matches = sorted(matches, key=itemgetter(2))
	# print matches in csv style.
	for match in matches:
		print("%d,%d,%f" % (match[0], match[1], match[2]))
