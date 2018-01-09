from PIL import ImageGrab,Image
import cv2
import numpy as np
import time
import math
import statistics as st


#Get each frame from the gta region


#With drawing the lanes, I am going to average out each poition of the hough to draw overall lanes
#Then I can seperate the lines


#Now send in the different end points of the line



#192 490
#348 378
#I am going to max out the averages,then average the max values then the current calc averages
#Find max and mins of the values

#IF we know the line of best fir, can't we use linear regression to rpedict the next points (Extrapolate)

def find_best_fit_right(x,y):
#Based on the array of the points in the line
#Find the line of best fit
	fit = np.polyfit(x,y,1)
	#This simplifies the y=mx+b formula to only one variable
	f = np.poly1d(fit)
	#This fits the
	x_new = np.linspace(min(x),max(x),10).astype(int)
	print x_new, 'right'
	x_extrapolate = min(x_new) - 20
	y_new = f(x_new).astype(int) #Doing the equation y=mx+b
	y_new_extrapolate = f(x_extrapolate).astype(int)
	points_new = list(zip(x_new,y_new))
	return (x_extrapolate,y_new_extrapolate),max(points_new)

def find_best_fit_left(x,y):
	fit = np.polyfit(x,y,1)
	f = np.poly1d(fit)
	x_new = np.linspace(min(x),max(x),10).astype(int)
	print x_new, 'left'
	x_extrapolate = max(x_new) + 20
	y_new = f(x_new).astype(int)
	y_new_extrapolate = f(x_extrapolate).astype(int)
	points_new = list(zip(x_new,y_new))
	#
	return (x_extrapolate,y_new_extrapolate), min(points_new)


def reset_points(a,b,c,d):
	a = []
	b = []
	c = []
	d = []
	return a,b,c,d

#A single indexed array that contains the end points of the line
xL = []
yL = []
xR = []
yR = []
nc = 0
def manage_lines(screen,lines):
	global xL
	global yL
	global xR
	global yR
	global nc
	nc += 1
	if nc % 25 == 0:xL,yL,xR,yR = reset_points(xL,yL,xR,yR)
	if nc == 1000:nc = 0
	for line in lines:
		for x1,y1,x2,y2 in line:
			slope = (y2 - y1)/(x2 - x1)
			if slope == -1:
			#Increasing x, decreasing y
				xL += [x1,x2]
				yL += [y1,y2]
				end,start = find_best_fit_left(xL,yL)
				cv2.line(screen,start,end,[255,255,255],3)
			elif slope == 0:
				xR += [x1,x2]
				yR += [y1,y2]
				end,start = find_best_fit_right(xR,yR)
				cv2.line(screen,start,end,[255,255,255],3)


def roi(screen, vertices):
	mask = np.zeros_like(screen,dtype=np.uint8)
	cv2.fillPoly(mask,np.int32([vertices]),255)
	masked_image = cv2.bitwise_and(screen, mask)
	return masked_image



def color_selection(screen):
	hls = cv2.cvtColor(screen,cv2.COLOR_RGB2HLS)
	lower_white = np.uint8([20,200,0])
	upper_white = np.uint8([255,255,255])
	#Now make a range for the white color
	white_color = cv2.inRange(hls,lower_white,upper_white)

	lower_yellow = np.uint8([10,50,100])
	upper_yellow = np.uint8([100,255,255])

	#Make the range for the yellow color
	yellow_color = cv2.inRange(hls,lower_yellow,upper_yellow)

	comb = cv2.bitwise_or(white_color,yellow_color)
	return cv2.bitwise_and(screen, screen, mask = comb)

def draw_circle(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONDBLCLK:
		print (x,y)

def processImage(org_screen):
	org_screen = color_selection(org_screen)
	org_screen = cv2.cvtColor(org_screen,cv2.COLOR_BGR2GRAY)
	org_screen = cv2.GaussianBlur(org_screen, (5,5), 0)
	org_screen = cv2.Canny(org_screen,50,160)
	vertices = np.array([[107,492],[382,343],[458,352],[720,491]])
	org_screen = roi(org_screen,vertices)
	lines = cv2.HoughLinesP(org_screen,2,np.pi/180,2,50,20)
	try:
		manage_lines(org_screen,lines)
	except:
		print 'none'
	return org_screen

def timer(cont):
	for i in range(cont):
		cont = cont - 1
		time.sleep(1)
		print (cont)

def main():
	timer(2)
	while 1:
		screen = np.array(ImageGrab.grab(bbox=(0,40,800,600)))
		screen = processImage(screen)
		cv2.imshow('window',screen)
		cv2.setMouseCallback('window',draw_circle)
		if cv2.waitKey(25) & 0xFF == ord('q'):
			cv2.destroyAllWindows()
			break



main()
