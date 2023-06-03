import numpy as np
import matplotlib.pyplot as plt
from core.calibration import calibration
from core.map_initialization import map_init_from_frames
from core.plane import get_dominant_plane
from core.projection import plot2D
from core.optical import optical_flow
from core.tracking import tracking
# import tracking


def work(video, args):
    print("worker.py : Start working!")
    # for i in range(16):
    #     plt.subplot(4, 4, i+1)
    #     plt.imshow(video[i])
    #     plt.axis("off")
    # plt.show()
    if args.calibration:
        K, _, _, _ = calibration(
            './core/data/calibration/video_mode/*.jpeg', 6, 10)  # (image path, gridx, gridy)
        print(K)
    else:
        # New extrinsic parmameters from 1920*1080 video camera
        K = np.array([[1.69428499e+03, 0.00000000e+00, 9.62922539e+02],
                      [0.00000000e+00, 1.70678063e+03, 5.20552346e+02],
                      [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
        # K = np.array([[3.10593801e+03, 0.00000000e+00, 1.53552466e+03],
        #               [0.00000000e+00, 3.08841292e+03, 2.03002207e+03],
        #               [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    C = Camera(K)

    M = map_init_from_frames(video[0], video[1], args.NNDR_RATIO, C.K)

    M = get_dominant_plane(M, video[0], C.K)

    for i in range(1, video.shape[0]-1):
        FP = optical_flow(video[i], video[i+1], M, C)
        C = tracking(FP, C)
        print(C.pose)


class Camera:
    def __init__(self, K):
        self.K = K
        self.R = np.eye(3)
        self.t = np.array([[-10], [0], [0]])
        Rt = np.concatenate((self.R, self.t), 1)
        self.pose = np.concatenate((Rt, [[0, 0, 0, 1]]), 0)