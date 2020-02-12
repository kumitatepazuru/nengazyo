import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import ocr

matplotlib.use('tkagg')


def ninsiki(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.RETR_LIST)
    new_img = img.copy()
    # plt.subplot(1, 5, 1)
    # plt.imshow(cv2.drawContours(new_img, contours, -1, (128, 0, 0), 30))

    menseki = []

    for i in range(0, len(contours)):
        menseki.append([contours[i], cv2.contourArea(contours[i])])

    menseki.sort(key=lambda x: x[1], reverse=True)

    epsilon = 0.1 * cv2.arcLength(menseki[0][0], True)
    approx = cv2.approxPolyDP(menseki[0][0], epsilon, True)
    cv2.drawContours(new_img, contours, -1, (128, 0, 0), 2)
    cv2.drawContours(new_img, approx, -1, (0, 0, 255), 15)
    return new_img, approx


def henkan(img):
    ksize = 19
    img = img.repeat(4, axis=0).repeat(4, axis=1)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, new_img = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    print(ret)
    new_img = cv2.medianBlur(new_img, ksize)
    new_img = cv2.medianBlur(new_img, ksize)
    new_img = cv2.medianBlur(new_img, ksize)
    kernel = np.ones((10, 10), np.float32) / 100
    new_img = cv2.filter2D(new_img, -1, kernel)
    # new_img = cv2.bilateralFilter(new_img, 5, 40, 40)
    kernel = np.ones((6, 6), np.uint8)
    # new_img = cv2.erode(new_img, kernel)
    new_img = cv2.erode(new_img, kernel)
    new_img = cv2.erode(new_img, kernel)
    new_img = cv2.erode(new_img, kernel)
    return new_img


def getNearestValue(lists, num):
    """
    概要: リストからある値に最も近い値を返却する関数
    @param lists: データ配列
    @param num: 対象値
    @return 対象値に最も近い値
    """

    # リスト要素と対象値の差分を計算し最小値のインデックスを取得
    idx = np.abs(np.asarray(lists) - num).argmin()
    return lists[idx]


def imagedataget(img):
    approx = ninsiki(img)[1]

    approx = approx.tolist()

    left = sorted(approx, key=lambda x: x[0])[:2]
    right = sorted(approx, key=lambda x: x[0])[2:]

    left_down = sorted(left, key=lambda x: x[0][1])[0]
    left_up = sorted(left, key=lambda x: x[0][1])[1]

    right_down = sorted(right, key=lambda x: x[0][1])[0]
    right_up = sorted(right, key=lambda x: x[0][1])[1]

    # print(left_down, left_up, right_down, right_up)
    perspective1 = np.float32([left_down, right_down, right_up, left_up])
    perspective2 = np.float32([[0, 0], [1378, 0], [1378, 2039], [0, 2039]])

    psp_matrix = cv2.getPerspectiveTransform(perspective1, perspective2)
    img_psp = cv2.warpPerspective(img, psp_matrix, (1378, 2039))

    # plt.subplot(1, 5, 3)
    # plt.imshow(img_psp)

    x = 550
    y = 0
    w = 500
    h = 150
    imgar = img_psp[y: y + h, x: x + w]
    new_img = imgar.copy()
    # plt.subplot(1, 5, 4)
    # plt.imshow(new_img)
    # plt.show()

    x = 880
    # x = 100
    y = 1830
    w = 450
    h = 150
    imgar = img_psp[y: y + h, x: x + w]
    return left_down, left_up, right_down, right_up, new_img, imgar


def run(img, filename=""):
    oldimg = img
    try:
        xydata = imagedataget(img)
    except IndexError:
        print("認識できません", filename)
        return [filename, "error", "------"]

    img_text = Image.fromarray(np.uint8(xydata[4]))
    ocr_jpn = ocr.ocr("jpn_best", "text")
    text1 = ocr_jpn.ocr(img_text)
    print(text1)
    if "は が き" in text1:
        pass
    else:
        img = np.rot90(img, 2)
        try:
            xydata = imagedataget(img)
        except IndexError:
            print("認識できません", filename)
            return [filename, "error", "------"]

        img_text = Image.fromarray(np.uint8(xydata[4]))
        text2 = ocr_jpn.ocr(img_text)
        print(text2)
        if "は が き" in text2:
            pass
        else:
            img = np.rot90(img, 1)
            try:
                xydata = imagedataget(img)
            except IndexError:
                print("認識できません", filename)
                return [filename, "error", "------"]
            img_text = Image.fromarray(np.uint8(xydata[4]))
            text3 = ocr_jpn.ocr(img_text)
            print(text3)
            if "は が き" in text3:
                pass
            else:
                img = np.rot90(img, 2)
                try:
                    xydata = imagedataget(img)
                except IndexError:
                    print("認識できません", filename)
                    return [filename, "error", "------"]

    new_img = henkan(xydata[5])
    img_text = Image.fromarray(np.uint8(new_img))
    # plt.subplot(1, 5, 5)
    plt.imshow(new_img, "gray")
    # plt.savefig("numbers/file.svg")
    ocr_eng = ocr.ocr("num+num1+num2+num3+num4+num5", "digit")
    # ocr_rot = ocr.ocr("jpn", "rotate")
    # rot = ocr_rot.ocr(img_text)
    # print(rot)
    # new_img = rotate(new_img, rot)
    # img_text = Image.fromarray(np.uint8(new_img))
    text = ocr_eng.ocr(img_text)
    print(text)
    if len(text) != 6:
        if "郵" in text1 or "便" in text1 or "は" in text1 or "が" in text1 or "き" in text1:
            img = oldimg
            try:
                xydata = imagedataget(img)
            except IndexError:
                print("認識できません", filename)
                return [filename, "error", "------"]
        elif "郵" in text2 or "便" in text2 or "は" in text2 or "が" in text2 or "き" in text2:
            img = np.rot90(oldimg, 2)
            try:
                xydata = imagedataget(img)
            except IndexError:
                print("認識できません", filename)
                return [filename, "error", "------"]
        elif "郵" in text3 or "便" in text3 or "は" in text3 or "が" in text3 or "き" in text3:
            img = np.rot90(oldimg, 3)
            try:
                xydata = imagedataget(img)
            except IndexError:
                print("認識できません", filename)
                return [filename, "error", "------"]
        else:
            print("認識できません", filename)
            return [filename, "error", "------"]
        new_img = henkan(xydata[5])
        img_text = Image.fromarray(np.uint8(new_img))
        # plt.subplot(1, 5, 5)
        plt.imshow(new_img, "gray")
        text = ocr_eng.ocr(img_text)
        print(text)
        if len(text) != 6:
            print("認識できません", filename)
            return [filename, "error", "------"]
    # plt.show()
    return [filename, "ok", text]


# for i in glob.glob("./images/*"):
#     a = time.time()
#     print(i)
#     ret = run(np.array(Image.open(i)), i)
#     b = time.time()
#     print(b - a, "s")
#     if ret[1] == "ok":
#         plt.show()

#print(run(np.array(Image.open("./images/P_20200101_181459.jpg"))))
# plt.show()

if __name__ == '__main__':
    camera = cv2.VideoCapture(0)  # カメラCh.(ここでは0)を指定
    cv2.namedWindow("camera", cv2.WINDOW_NORMAL)

    # 撮影＝ループ中にフレームを1枚ずつ取得（qキーで撮影終了）
    while True:
        ret, frame = camera.read()  # フレームを取得
        try:
            frame = ninsiki(frame)[0]
            cv2.imshow("camera", frame)
        except IndexError:
            pass

        key = cv2.waitKey(1) & 0xFF
        # キー操作があればwhileループを抜ける
        if key == ord('q'):
            break
        if key == ord("p"):
            run(frame, "webcamphoto")

    # 撮影用オブジェクトとウィンドウの解放
    camera.release()
    cv2.destroyAllWindows()
