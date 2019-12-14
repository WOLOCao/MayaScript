# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-03 22:02:34'

""" 
任意曲线控制器 转 骨骼方块曲线控制器
2.0 直接替换 shape 而不修改 transform 节点
"""

import pymel.core as pm
import pymel.core.datatypes as dt
import math

def generateCubeFromVector(start_pt,end_pt,origin=None,distant=3):

    if origin:
        matrix = origin.worldMatrix.get().inverse()
        start_pt = start_pt*matrix
        end_pt = end_pt*matrix
    
    x_vec = start_pt - end_pt
    y_vec = dt.Vector([0,1,0])
    y_vec = y_vec.rotateBy(x_vec,math.pi/4)
    z_vec = dt.Vector([0,0,1])
    z_vec = z_vec.rotateBy(x_vec,math.pi/4)

    # NOTE 计算8个顶点坐标位置
    start_corner_1 = (start_pt+y_vec*distant)
    start_corner_2 = (start_pt-y_vec*distant)
    start_corner_3 = (start_pt+z_vec*distant)
    start_corner_4 = (start_pt-z_vec*distant)

    end_corner_1 = (end_pt+y_vec*distant)
    end_corner_2 = (end_pt-y_vec*distant)
    end_corner_3 = (end_pt+z_vec*distant)
    end_corner_4 = (end_pt-z_vec*distant)

    # NOTE 生成方块曲线
    return pm.curve(d=1,p=[
        start_corner_1,
        start_corner_3,
        start_corner_2,
        start_corner_4,
        start_corner_1,
        end_corner_1,
        end_corner_3,
        end_corner_2,
        end_corner_4,
        end_corner_1,
        end_corner_4,
        start_corner_4,
        start_corner_2,
        end_corner_2,
        end_corner_3,
        start_corner_3,
    ])
    

def replaceController2Cube(distant=3):
        
    for origin in pm.ls(sl=1,v=1,ni=1):
        origin_shape = origin.getShape(type="nurbsCurve")
        if not origin_shape: 
            pm.warning(u"找不到曲线 %s" % origin)
            pm.headsUpMessage(u"找不到曲线 %s" % origin)
            continue

        jnt_list = []
        for constraint in set(origin.listConnections(type="constraint")):
            if constraint.type() in ["aimConstraint","tangentConstraint","normalConstraint"]:
                continue

            for jnt in constraint.listConnections(type='joint'):
                if jnt not in jnt_list:
                    jnt_list.append(jnt)

        try:
            start_jnt = jnt_list[0]
            start_pt = start_jnt.getTranslation(space="world")
            origin_pt = origin.getTranslation(space="world")
            if (start_pt - origin_pt).length() > 0.01:
                raise RuntimeError()
            child_list = pm.ls(start_jnt,dag=1,type="joint")
            end_jnt = child_list[1]
            end_pt = end_jnt.getTranslation(space="world")
            crv = generateCubeFromVector(start_pt,end_pt,origin,distant=distant)
        except:
            start_pt = dt.Point(-distant,0,0)
            end_pt = dt.Point(distant,0,0)
            crv = generateCubeFromVector(start_pt,end_pt,distant=distant)

        shape = crv.getShape()
        # NOTE 设置颜色
        if origin_shape.overrideEnabled.get():
            shape.overrideEnabled.set(1)
            if origin_shape.overrideRGBColors.get():
                color = origin_shape.overrideColorRGB.get()
                shape.overrideColorRGB.set(color)
            else:
                color = origin_shape.overrideColor.get()
                shape.overrideColor.set(color)

        pm.parent(shape,origin,r=1,s=1)
        pm.delete(crv)
        pm.delete(origin_shape)


if __name__ == "__main__":
    replaceController2Cube()