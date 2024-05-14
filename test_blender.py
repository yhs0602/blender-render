import bpy

# 모든 객체 선택 해제
bpy.ops.object.select_all(action="DESELECT")

# 기본 큐브 객체 선택 후 삭제
if "Cube" in bpy.data.objects:
    bpy.data.objects["Cube"].select_set(True)
    bpy.ops.object.delete()

# 새 큐브 추가
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

print("Script executed successfully")
