# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-03 10:07:09'

"""
overlapper 插件改良
"""

from maya import cmds
import random
# from PySide2 import QtGui
# from PySide2 import QtCore
# from PySide2 import QtWidgets

# class overlapperWin(QtWidgets.QWidget):
    
#     def __init__(self):
#         super(overlapper,self).__init__()
#         self.controller_list = []
        

#     def setUpLocator(self):
#         self.controller_list = cmds.ls(sl=1)
#         jnt_list = []
#         for i,controller in enumerate(self.controller_list):
#             pos = controller.getTranslation(space="world")
#             cmds.joint(p=pos,rad=1,n="%s_OverlapJoint" % controller)



# if __name__ == "__main__":
#     main

# cmds.delete("*_OverlapJoint")

def main():
        
    overlapIntensity = 1.0
    timeShift = 3.0

    WindSwitch = False
    windScaleValue = 3.0
    windSpeedValue = 1.0

    TRANSLATEmode = False
    
    CycleCheckBox = True

    timeStart = cmds.playbackOptions(q=1,min=1)
    timeEnd = cmds.playbackOptions(q=1,max=1)

    controller_list = cmds.ls(sl=1)

    # NOTE 生成骨骼 | 调整轴向
    jnt_list = []
    cmds.select(cl=1)
    for i,controller in enumerate(controller_list):
        # controller.getRotatePivot(space="world")
        pos = cmds.xform(controller,q=1,rp=1,ws=1) 
        jnt = cmds.joint(p=pos,rad=1,n="%s_OverlapJoint" % controller)
        if i > 0:
            cmds.joint(_jnt,e=1,zso=1,oj="xyz",sao="yup")
        jnt_list.append(jnt)
        _jnt = jnt

    last_jnt = cmds.duplicate(jnt,rr=1,n="%s_LastOrientJoint" % controller)[0]
    cmds.move(2,0,0,r=1,ls=1,wd=1)
    cmds.parent(last_jnt,jnt)
    jnt_list.append(last_jnt)
    cmds.joint(jnt,e=1,zso=1,oj="xyz",sao="yup")

    # NOTE 生成骨骼 | 调整轴向
    sumLenghtJoints = sum([cmds.getAttr("%s.tx" % jnt) for jnt in jnt_list])
    averageLenghtJoints = (sumLenghtJoints - 2) / len(jnt_list)

    # last_jnt.tx.set(averageLenghtJoints)
    cmds.setAttr( last_jnt + ".tx",averageLenghtJoints)
    constraint_list = []
    for controller,jnt in zip(controller_list,jnt_list):
        constraint_list.extend(cmds.pointConstraint(controller,jnt,mo=1))
        constraint_list.extend(cmds.orientConstraint(controller,jnt,mo=1))
    
    # bake
    cmds.bakeResults(
        jnt_list,
        simulation = 1,
        t = (timeStart,timeEnd),
        sampleBy = 1, 
        disableImplicitControl = 1, 
        preserveOutsideKeys = 0, 
    )
    
    cmds.delete(constraint_list)

    if CycleCheckBox:
        for i,jnt in enumerate(jnt_list):
            # if i == len(controller_list) - 1:
            #     continue

            cmds.selectKey(
                cmds.listConnections(jnt+".tx",type="animCurve"),
                cmds.listConnections(jnt+".ty",type="animCurve"),
                cmds.listConnections(jnt+".tz",type="animCurve"),
                cmds.listConnections(jnt+".rx",type="animCurve"),
                cmds.listConnections(jnt+".ry",type="animCurve"),
                cmds.listConnections(jnt+".rz",type="animCurve"),
                r=1,k=1,t=(timeStart,timeEnd))
            cmds.copyKey()
            cmds.pasteKey(time=(timeEnd,timeEnd),float=(timeEnd,timeEnd),option="insert",copies=2,connect=0,timeOffset=0,floatOffset=0,valueOffset=0)
        
        cycleLenghts = timeEnd - timeStart
        timeEnd = timeEnd + 2*cycleLenghts

    
    # NOTE 进行 overlap
    overlapIntensityMult = averageLenghtJoints/overlapIntensity*5
    timeShiftNeg = -timeShift
    timeShiftCurrent = 1+timeShift

    out_list = []
    for i,[controller,jnt] in enumerate(zip(controller_list,jnt_list)):

        IK_loc = cmds.spaceLocator(n="overlapOffsetIKLocator%s"%i)[0]
        cmds.delete(cmds.parentConstraint(jnt,IK_loc,w=1))
        offset_loc = cmds.spaceLocator(n="overlapOffsetLocator%s"%i)[0]
        cmds.delete(cmds.parentConstraint(jnt,offset_loc,w=1))

        cmds.move(overlapIntensityMult,0,0,r=1,os=1,ls=1)
        con_1 = cmds.parentConstraint(jnt,offset_loc,mo=1)
        con_2 = cmds.parentConstraint(jnt,IK_loc,mo=1)

        # bake
        # filter curve
        cmds.bakeResults(
            offset_loc,IK_loc,
            simulation = 0,
            t = (timeStart,timeEnd),
            sampleBy = 1, 
            disableImplicitControl = 1, 
            preserveOutsideKeys = 1, 
        )

        cmds.delete(con_1,con_2)

       
        
        # NOTE 过滤关键帧曲线
        cmds.filterCurve(
            (offset_loc+"_rotateX"),
            (offset_loc+"_rotateY"),
            (offset_loc+"_rotateZ")
        )
        wind_loc = cmds.spaceLocator(n="overlapOffsetLocatorWind%s"%i)[0]
        cmds.parent(wind_loc,offset_loc)
        cmds.makeIdentity(wind_loc,a=0,t=1,r=1,s=1,n=0,pn=1)
        
        cmds.keyframe((IK_loc+"_translateX"),e=1,iub=1,r=1,o="over",tc=timeShift)
        cmds.keyframe((IK_loc+"_translateY"),e=1,iub=1,r=1,o="over",tc=timeShift)
        cmds.keyframe((IK_loc+"_translateZ"),e=1,iub=1,r=1,o="over",tc=timeShift)
        cmds.keyframe((offset_loc+"_translateX"),e=1,iub=1,r=1,o="over",tc=timeShift)
        cmds.keyframe((offset_loc+"_translateY"),e=1,iub=1,r=1,o="over",tc=timeShift)
        cmds.keyframe((offset_loc+"_translateZ"),e=1,iub=1,r=1,o="over",tc=timeShift)
        cmds.keyframe((offset_loc+"_rotateX"),e=1,iub=1,r=1,o="over",tc=timeShift)
        cmds.keyframe((offset_loc+"_rotateY"),e=1,iub=1,r=1,o="over",tc=timeShift)
        cmds.keyframe((offset_loc+"_rotateZ"),e=1,iub=1,r=1,o="over",tc=timeShift)

        cmds.selectKey((IK_loc+"_translateX"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))
        cmds.selectKey((IK_loc+"_translateY"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))
        cmds.selectKey((IK_loc+"_translateZ"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))
        cmds.selectKey((offset_loc+"_translateX"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))
        cmds.selectKey((offset_loc+"_translateY"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))
        cmds.selectKey((offset_loc+"_translateZ"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))
        cmds.selectKey((offset_loc+"_rotateX"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))
        cmds.selectKey((offset_loc+"_rotateY"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))
        cmds.selectKey((offset_loc+"_rotateZ"),add=1,k=1,t=(timeShiftCurrent,timeShiftCurrent))

        cmds.keyframe(animation="keys",option="over",relative=1,timeChange=timeShiftNeg)

        first_loc = cmds.spaceLocator(n="overlapInLocator_first_%s"%i)[0]
        result_loc = cmds.spaceLocator(n="overlapResultLocator_%s"%i)[0]
        second_loc = cmds.spaceLocator(n="overlapInLocator_second_%s"%i)[0]
        cmds.parent(first_loc,jnt)
        cmds.parent(result_loc,jnt)
        cmds.parent(second_loc,jnt)

        cmds.makeIdentity(first_loc,second_loc,result_loc,a=0,t=1,r=1,s=1,n=0,pn=1)

        cmds.move(overlapIntensityMult,0,0,r=1,os=1,ls=1)

        aim_grp = cmds.group(first_loc,n=first_loc+"grp")
        
        if TRANSLATEmode:
            cmds.pointConstraint(IK_loc,first_loc,mo=1)

        cmds.parentConstraint(wind_loc,second_loc,mo=1)

        cmds.aimConstraint(second_loc,aim_grp,mo=1,aimVector=[1,0,0],upVector=[0,1,0],worldUpType="object",worldUpObject=second_loc)
        cmds.orientConstraint(second_loc,first_loc,mo=1,skip=["y","z"],w=1)
        cmds.parentConstraint(first_loc,result_loc,mo=1)

        if WindSwitch :
            windMultiply = 0.07*overlapIntensityMult*windScaleValue
            speedMultiply = 20/windSpeedValue; 

            cmds.setKeyframe( wind_loc, attribute=['translateY','translateZ'], t=[timeStart,timeStart] )

            cmds.bakeResults(
                wind_loc,
                simulation = 0,
                t = (timeStart,timeEnd+speedMultiply),
                sampleBy = speedMultiply, 
                oversamplingRate = 1, 
                disableImplicitControl = 1, 
                preserveOutsideKeys = 1, 
                at = ['ty','tz']
            )

            for attr in cmds.listAttr(wind_loc,k=1):
                animCurve = cmds.listConnections("%s.%s"%(wind_loc,attr),type="animCurve")
                if not animCurve:
                    continue
                for animCurveCurrent in animCurve:
                    for animCurveCurrentKeysTime in cmds.keyframe(animCurveCurrent,q=1,t=(timeStart,timeEnd),tc=1):
                        t = (animCurveCurrentKeysTime,animCurveCurrentKeysTime)
                        animCurveCurrentKeysTimeArray = cmds.keyframe(animCurveCurrent,q=1,time=t,vc=1)
                        RandomizerValue = random.random()*2 - 1
                        animCurveCurrentKeysValueArrayAddRandom = animCurveCurrentKeysTimeArray[0] + windMultiply*RandomizerValue
                        cmds.keyframe(animCurveCurrent,e=1,iub=1,r=1,o="over",vc=animCurveCurrentKeysValueArrayAddRandom,t=t)

            attr = (wind_loc+"_translateY")
            cmds.keyframe(attr,e=1,iub=1,r=1,o="over",tc=speedMultiply/2)
            t = (speedMultiply/2)+1
            cmds.selectKey(attr,add=1,k=1,t=(t,t))
            cmds.keyframe(attr,animation="keys",r=1,o="over",tc=speedMultiply/-2)
        
        cmds.bakeResults(
            result_loc,
            simulation = 0,
            t = (timeStart,timeEnd),
            sampleBy = 1, 
            disableImplicitControl = 1, 
            preserveOutsideKeys = 1, 
        )

        out_loc = cmds.spaceLocator(n="overlapResultLocatorOut_%s"%i)[0]
        cmds.parentConstraint(result_loc,out_loc,mo=1)

        cmds.bakeResults(
            out_loc,
            simulation = 0,
            t = (timeStart,timeEnd),
            sampleBy = 1, 
            disableImplicitControl = 1, 
            preserveOutsideKeys = 1, 
        )
        cmds.parentConstraint(out_loc,jnt,mo=1)
        out_list.append(out_loc)

    # cmds.progressWindow(ep=1)
    # return
    if CycleCheckBox:
        timeStart = cmds.playbackOptions(q=1,min=1)
        timeEnd = cmds.playbackOptions(q=1,max=1)
        cycleLenghts = timeEnd - timeStart
        for out_loc in out_list:
            cmds.keyframe((out_loc+"_translateX"),e=1,iub=1,r=1,o="over",tc=cycleLenghts*-2)
            cmds.keyframe((out_loc+"_translateY"),e=1,iub=1,r=1,o="over",tc=cycleLenghts*-2)
            cmds.keyframe((out_loc+"_translateZ"),e=1,iub=1,r=1,o="over",tc=cycleLenghts*-2)
            cmds.keyframe((out_loc+"_rotateX"),e=1,iub=1,r=1,o="over",tc=cycleLenghts*-2)
            cmds.keyframe((out_loc+"_rotateY"),e=1,iub=1,r=1,o="over",tc=cycleLenghts*-2)
            cmds.keyframe((out_loc+"_rotateZ"),e=1,iub=1,r=1,o="over",tc=cycleLenghts*-2)


if __name__ == "__main__":
    from timeit import timeit
    # print timeit("main()","from __main__ import main",number=1)
    main()
