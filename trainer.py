#!/usr/bin/python

import sys, time
import Xlib
import Image, ImageStat

import cv

from Xlib import X, display, Xutil, Xcursorfont, protocol, error
from Xlib.protocol import request

class Curveball:

    def __init__(self):
        pass

    def find_window(self):

        # get list of all the windows
        window_ids = root.get_full_property(mydisplay.intern_atom('_NET_CLIENT_LIST'), Xlib.X.AnyPropertyType).value

        # find the one that named 'curveball'
        for window_id in window_ids:
            
            window = mydisplay.create_resource_object('window', window_id)
            name = window.get_wm_name()
            pid = window.get_full_property(mydisplay.intern_atom('_NET_WM_PID'), Xlib.X.AnyPropertyType)

            print name

            if name.lower().find("curveball.swf") >= 0:
                self.geom = window.get_geometry()
                return True 
        
        return False 


    def get_image(self):

        x = self.geom.x
        y = self.geom.y
        w = self.geom.width
        h = self.geom.height

        ret = root.get_image(x, y, w, h, X.ZPixmap, 0xffffffff)
        if not ret:
            raise ValueError("Could not get_image! Returned %d" % ret)

        return Image.fromstring("RGBX", (w, h), ret.data, "raw", "BGRX").convert("RGB")

mydisplay = display.Display()
root = mydisplay.screen().root

curveball = Curveball()

if not curveball.find_window():
    print "Could not find curveball window. Exiting"
    sys.exit()
else:
    print "Found curveball window at (%s, %s) with size (%s, %s)" % (curveball.geom.x, curveball.geom.y, curveball.geom.width, curveball.geom.height)

# get initial image
pil_img = curveball.get_image()

cv_img = cv.CreateImageHeader(pil_img.size, cv.IPL_DEPTH_8U, 3)
g_img = cv.CreateImage(pil_img.size, cv.IPL_DEPTH_8U, 1)

cv.NamedWindow("Curveball Trainer", 1)
cv.NamedWindow("Curveball Trainer - Filtered", 1)

while True:

    t1 = time.time()

    pil_img = curveball.get_image()
    cv.SetData(cv_img, pil_img.tostring())

    cv.CvtColor(cv_img, cv_img, cv.CV_BGR2RGB)

    cv.Split(cv_img, None, g_img, None, None)

    cv.Threshold(g_img, g_img, 240, 255, cv.CV_THRESH_BINARY)

    cv.Erode(g_img, g_img, None, 1)

    storage = cv.CreateMemStorage(0)
    contour = cv.FindContours(g_img, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
    points = []

    while contour:
        bound_rect = cv.BoundingRect(list(contour))
        contour = contour.h_next()

        pt1 = (bound_rect[0], bound_rect[1])
        pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
        points.append(pt1)
        points.append(pt2)
        cv.Rectangle(cv_img, pt1, pt2, cv.CV_RGB(255,0,0), 1)
    
    if len(points):
        center_point = reduce(lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), points)
        cv.Line(cv_img, (center_point[0], 0),
                        (center_point[0], cv_img.height),
                        cv.CV_RGB(255,0,0), 1, cv.CV_AA, 0)
        cv.Line(cv_img, (0, center_point[1]),
                        (cv_img.width, center_point[1]),
                        cv.CV_RGB(255,0,0), 1, cv.CV_AA, 0)

        root.warp_pointer(curveball.geom.x + center_point[0], curveball.geom.y + center_point[1] + curveball.geom.height*0.015)

    cv.ShowImage("Curveball Trainer - Filtered", g_img)
    cv.ShowImage("Curveball Trainer", cv_img)

    k = cv.WaitKey(10)

    print time.time() - t1


