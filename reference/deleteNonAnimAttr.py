from maya import cmds

# NOTE C:\Program Files\Autodesk\Maya2017\scripts\others\referenceEditsWindow.mel
remove_dict = {
    "addAttr":lambda buffer: "%s.%s" % (buffer[-1],buffer[2]),
    "deleteAttr":lambda buffer: buffer[1],
    "setAttr":lambda buffer: buffer[1],
    "relationship":lambda buffer: buffer[2],
    "parent":lambda buffer: buffer[-1] if buffer[-2] == "-w" else buffer[-2],
}

cmds.progressWindow(	
        title='remove unreleated edits in reference' ,
        progress=0.0,
        isInterruptable=True )

count = len(cmds.ls(references=1))
for i,ref in enumerate(cmds.ls(references=1)):
    
    if cmds.progressWindow( query=True, isCancelled=True ) :
        cmds.progressWindow(endProgress=1)
        break
    amount = float(i)/count*100
        
    cmds.progressWindow( e=1, progress=amount,status='%s' % i)

    # NOTE 获取引用文件的名称
    try:
        file_name = cmds.referenceQuery( ref,filename=1,unresolvedName=1 )
    except:
        continue

    # NOTE 查询文件是否加载进场景中
    referenceUnloaded = cmds.file(file_name,q=1,dr=1)

    # NOTE 获取当前引用节点的编辑信息
    for edit in cmds.referenceQuery( ref,editStrings=True,showDagPath=1 ):
        buffer = edit.split()
        command,attr = buffer[:2]

        # NOTE 根据 referenceEditsWindow.mel 的处理来区分类型的引用调用的代码
        connectAttr = False
        if command == "disconnectAttr":
            remove_attr = buffer[-2] if referenceUnloaded else buffer[-1]
        elif command == "connectAttr":
            connectAttr = True
            remove_attr = "%s,%s" % (buffer[1],buffer[2])
        else:
            remove_attr = remove_dict[command](buffer)
        
        remove_attr = remove_attr.replace('"','')

        dagPath = remove_attr.split('.')[0].replace('"', '') if connectAttr == True else remove_attr.split('.')[0].replace('"', '')
        # NOTE 如果物体不存在则跳过处理
        if not cmds.objExists(dagPath):
            continue
        objectType = cmds.objectType(dagPath)
        # NOTE 过滤 transform 节点 和 动画曲线的处理
        if objectType != 'transform' and 'animCurve' not in objectType:
            if connectAttr:
                cmds.referenceEdit( *remove_attr.split(","), editCommand=command, failedEdits = True, successfulEdits = True, removeEdits = True )
            else:
                cmds.referenceEdit( remove_attr, editCommand=command, failedEdits = True, successfulEdits = True, removeEdits = True )

