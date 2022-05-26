import dearpygui.dearpygui as dpg
import cv2
import numpy as np
import time

def save_callback():
    print("Save Clicked")

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()



threshold_binary = 127
ROI = None


# https://github.com/Pcothren/DearPyGui-Examples/blob/main/camera_capture_with_opencv.py

def convertImg(grayimg):
    img = cv2.cvtColor(grayimg, cv2.COLOR_GRAY2BGR)
    data = np.flip(img, 2)
    data = data.ravel()
    data = np.asfarray(data, dtype='f')
    texture_data = np.true_divide(data, 255.0)
    return texture_data


frame = cv2.imread("123.jpg", 0)
width = frame.shape[1]
height = frame.shape[0]

with dpg.texture_registry():
    dpg.add_raw_texture(width, height, convertImg(frame), tag="texture_tag", format=dpg.mvFormat_Float_rgb)
    dpg.add_raw_texture(width, height, convertImg(frame), tag="ROI_texture", format=dpg.mvFormat_Float_rgb)

img_ROI = None
def process_img():
    global ROI, frame, threshold_binary, img_ROI
    frame_mod = frame.copy()
    height, width = frame.shape
    x_min, x_max, y_min, y_max = [int(x) for x in ROI]
    ret, frame_gray = cv2.threshold(frame_mod, threshold_binary, 255, cv2.THRESH_BINARY)
    img_ROI = frame_gray[height-y_max:height-y_min, x_min:x_max]
    print((np.sum(img_ROI / 255) / np.pi)**0.5 )
    # frame_result = frame_gray[height - y_min:height - y_max, width - x_min: width - x_max]


    dpg.set_value("ROI_texture", convertImg(frame_gray))



def query(sender, app_data, user_data):
    global ROI, frame, threshold_binary
    if ROI != app_data:
        x_min, x_max, y_min, y_max = [int(x) for x in app_data]
        ROI = app_data
        dpg.set_axis_limits("XAxis", app_data[0], app_data[1])
        dpg.set_axis_limits("YAxis", app_data[2], app_data[3])
        process_img()


def change_threshold(sender, app_data, user_data):
    global threshold_binary
    threshold_binary = app_data
    process_img()

def save_output(sender, app_data, user_data):
    global img_ROI
    cv2.imwrite("output.jpg", img_ROI)
    print("Save OK")


with dpg.window(label="Example Window", width = 450, height = 450, no_close = True):
    with dpg.plot(height=400, width=400, callback =query, query = True, equal_aspects = True):
        dpg.add_plot_axis(dpg.mvXAxis)
        dpg.add_plot_axis(dpg.mvYAxis, tag="y_axis")
        dpg.add_image_series("texture_tag", [0,0], [width, height], label = "Img", parent = "y_axis")

with dpg.window(label="Binary Fitting", width = 450, height = 480, pos = (460, 0), no_close = True):
    dpg.add_slider_int(tag = "threshold", label="Threshold",min_value = 0,  max_value=255, callback=change_threshold)
    dpg.set_value("threshold", 127)
    dpg.add_button(label="Save", callback=save_output)
    with dpg.plot(height=400, width=400, equal_aspects = True):
        dpg.add_plot_axis(dpg.mvXAxis, tag = "XAxis")
        dpg.add_plot_axis(dpg.mvYAxis, tag= "YAxis")
        dpg.add_image_series("ROI_texture", [0,0], [width, height], label = "Img", parent = "YAxis")





dpg.show_viewport()
dpg.start_dearpygui()
while dpg.is_dearpygui_running():
    time.sleep(0.1)

dpg.destroy_context()