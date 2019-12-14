# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-10 09:49:26'

"""
快速对旋转属性制作 权重舞
"""

import pymel.core as pm

# NOTE 提取K帧属性
keyframe_list = []
attr_list = ['rx','ry','rz']
for ctrl in cmds.ls(sl=1):
    for attr in attr_list:
        attr = pm.Attribute("%s.%s"%(ctrl,attr))
        if attr.isKeyable() and not attr.isLocked() and not attr.isHidden():
            keyframe_list.append(attr)

frame = 0    
for i,attr in enumerate(keyframe_list):
    attr.setKey(v=0,t=frame)
    attr.setKey(v=90,t=frame+5)
    attr.setKey(v=0,t=frame+10)
    attr.setKey(v=-90,t=frame+15)
    attr.setKey(v=0,t=frame+20)
    frame = frame+20
