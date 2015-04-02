#!/usr/bin/env python

import numpy as np
import Image

def d(im1, im2, p=2):
	y1,x1 = im1.shape
	y2,x2 = im2.shape
	if (y1,x1) != (y2,x2):
		#print "Images must be the same size."
		#print "Image 1:", x1, "x", y1
		#print "Image 2:", x2, "x", y2
		return -1
	else:
		#print "Image size:", x1, "x", y1
		distance = 0
		for a in range(x1):
			for b in range(y1):
				distance += abs(im1[b][a]-im2[b][a])**p
		return (distance/(x1*y1))**(1.0/p)

def TestD():
	i1 = np.array(Image.open("checker.jpg").convert('L'),dtype="float")
	i2 = np.array(Image.open("checker_grad.jpg").convert('L'),dtype="float")
	i3 = np.array(Image.open("checker_blur.jpg").convert('L'),dtype="float")

	# test1: distance between image and itself
	d11 = d(i1,i1)
	d22 = d(i2,i2)
	print "\nd(i1,i1) =", d11
	print "d(i2,i2) =", d22

	# test2: symmetry
	d12 = d(i1,i2)
	d21 = d(i2,i1)
	print "\nd(i1,i2) =", d12
	print "d(i2,i1) =", d21

	# test3: triangle inequality
	d23 = d(i2,i3)
	d13 = d(i1,i3)
	print "\nd(i1,i2) =", d12
	print "d(i2,i3) =", d23
	print "d(i1,i3) =", d13
	print "d(i1,i3) =< d(i1,i2) + d(i2,i3)"
	print "d(i1,i3) >= abs(d(i1,i2) - d(i2,i3))"
	print abs(d(i1,i2) - d(i2,i3)), "<=", d(i1,i3), "<=", d(i1,i2) + d(i2,i3), "\n"

if __name__ == "__main__":
	TestD()
