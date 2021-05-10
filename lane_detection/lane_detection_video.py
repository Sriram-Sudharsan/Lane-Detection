import numpy as np
import cv2
import copy
import traceback
import math
from common_functions import *

def main():
    cap = cv2.VideoCapture('/home/linlite/Desktop/lane-detection-and-turn-prediction/challenge_video.mp4')
    prev_lines = None
    prev_line_coordinates = []
    warping_coordinates_present = False
    cv2.imshow("gg",cap)
   # ourcc = cv2.VideoWriter_fourcc('F','M','P','4')

    #out = cv2.VideoWriter("problem3_lane_detection.avi", fourcc, 20.0, (1280, 720))

    while cap.isOpened():
        
        try:
            
            ret, frame = cap.read()
            image = frame
            if not ret or cv2.waitKey(1) == 27:
                break


            height, width = image.shape[:2]
            # Correct the  distortion

            #Camera Matrix
            K = np.array([[  1.15422732e+03,0.00000000e+00,6.71627794e+02],
                        [  0.00000000e+00,1.14818221e+03,3.86046312e+02],
                        [  0.00000000e+00,0.00000000e+00,1.00000000e+00]])

            #Distortion Coefficients
            dist = np.array([[ -2.42565104e-01,  -4.77893070e-02,  -1.31388084e-03,  -8.79107779e-05,
                2.20573263e-02]])

            image_undistorted = cv2.undistort(image, K, dist)
            image_blurred = cv2.medianBlur(image_undistorted, 5)

            roi_vertices = [
                (0,height),
                (width,height),
                (width,int(0.60*height)),
                (0,int(0.60*height))]


            roi_image = roi(image_blurred, np.array([roi_vertices],np.int32))

            image_white_yellow, w, y = select_white_yellow(roi_image)
            gray = cv2.cvtColor(image_white_yellow.astype(np.uint8), cv2.COLOR_RGB2GRAY)
            canny_edges = cv2.Canny(gray,100, 200)

            white_yellow_mask_bin = np.zeros((image_white_yellow.shape[0], image_white_yellow.shape[1]))
            white_yellow_mask_bin[(image_white_yellow[:, :, 0] == 255)] = 1
            
            
            kernel = np.ones((5,5),np.uint8)
            white_yellow_mask_bin = cv2.morphologyEx(white_yellow_mask_bin, cv2.MORPH_CLOSE, kernel)

            lines = cv2.HoughLinesP(canny_edges,
                                    rho=6,
                                    theta=np.pi/60,
                                    threshold=200,
                                    lines=np.array([]),
                                    minLineLength=40,
                                    maxLineGap=25)

            if lines is not None:
                image_lines, line_coordinates = draw_lines(image, lines)
                prev_lines = copy.deepcopy(lines)
                prev_line_coordinates = line_coordinates
                no_lines = False
            
            elif prev_lines is not None:
                image_lines, line_coordinates = draw_lines(image, prev_lines)
                
                no_lines = False
            else:
                print('no lines detected')
                no_lines = True
                
            if len(line_coordinates) > 0:
                if not warping_coordinates_present:
                    src_points, dest_points, dest_img_size = get_src_destpoints_for_warping(image,line_coordinates)
                    warping_coordinates_present = True
                warped_image, overlayed_image, turn = warp_and_process_image(image_lines, line_coordinates, src_points, dest_points, dest_img_size, image_white_yellow)
            else:
                no_lines = True


            
            if not no_lines:
                if turn is not None:
                    cv2.putText(overlayed_image,('Expected turn = '+str(turn)),(50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2,cv2.LINE_AA)
            cv2.imshow("Detection", overlayed_image)
            out.write(overlayed_image)
            cv2.imshow("roi", roi_image)
            cv2.imshow("white_yellow", image_white_yellow)
            cv2.imshow("edges", canny_edges)
            cv2.imshow("O", image)
        except:
            traceback.print_exc()
            break
        

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
    
