# coding:utf-8

import tensorflow as tf
import numpy as np
from PIL import Image
from code.code_21 import mnist_lenet5_backward as mnist_backward, mnist_lenet5_forward as mnist_forward
from utils.result import Result
from config import config
import os


def restore_model(testPicArr):
    with tf.Graph().as_default() as tg:
        x = tf.placeholder(tf.float32, [
            1,
            mnist_forward.IMAGE_SIZE,
            mnist_forward.IMAGE_SIZE,
            mnist_forward.NUM_CHANNELS])
        y = mnist_forward.forward(x, False, None)
        # 输出节点的卷积值
        # preValue =y# tf.argmax(y,1)
        preValue = tf.nn.softmax(y)

        variable_averages = tf.train.ExponentialMovingAverage(mnist_backward.MOVING_AVERAGE_DECAY)
        variables_to_restore = variable_averages.variables_to_restore()
        saver = tf.train.Saver(variables_to_restore)

        with tf.Session() as sess:


            ckpt = tf.train.get_checkpoint_state(mnist_backward.MODEL_SAVE_PATH)

            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess,  ckpt.model_checkpoint_path)

                testPicArr =np.resize(testPicArr,(1,28,28,1))
                preValue = sess.run(preValue, feed_dict={x: testPicArr})
                return preValue
            else:
                print("No checkpoint file found")
                return -1

# 二值化函数
def pre_pic(picName):
    img = Image.open(picName)
    reIm = img.resize((28, 28), Image.ANTIALIAS)
    im_arr = np.array(reIm.convert('L'))
    threshold = 125  #阙值

    for i in range(28):
        for j in range(28):
            im_arr[i][j] = 255 - im_arr[i][j]
            if (im_arr[i][j] < threshold):
                im_arr[i][j] = 0
            else:
                im_arr[i][j] = 255
    # print(im_arr)
    nm_arr = im_arr.reshape([1, 784])
    nm_arr = nm_arr.astype(np.float32)
    img = np.multiply(nm_arr, 1.0 / 255.0)
    # print(img
    return img

def application(picPath):
    # 判断是否能打开
    if os.path.exists(picPath):

        testPicArr = pre_pic(picPath)  # 预处理，二值化图片
        preValue = restore_model(testPicArr)  # 神经网络识别
        # print(preValue)  # 输出节点卷积值
        # 取输出节点卷积值的逆序前3位
        dic = {i : preValue[0][i] for i in range(len(preValue[0]))}
        a1 = sorted(dic.items(), key=lambda x: x[1], reverse=True)

        jresult = Result("true",None,None,None,picPath)
        for i in range(20):
            jresult.matrix[i][0]=a1[i][0]
            jresult.matrix[i][1] = a1[i][1]

    else:
        jresult = Result("false", None, None,'reg error',picPath)
    return jresult

def main():
    for i in range(6):
        jr = application(config.PROJECT_PATH+"/test_pic/pic_21/"+str(i)+".png")
        print(jr.tostring())
if __name__ == '__main__':
    main()
