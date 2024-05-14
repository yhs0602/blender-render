import random

import bpy
import math
import pathlib

# 설정 값
current_dir = pathlib.Path(__file__).parent.absolute()
output_dir = current_dir / "output"
blend_file_path = "/Users/yanghyeonseo/Downloads/shelf.blend"
if not output_dir.exists():
    output_dir.mkdir()

num_frames = 36  # 렌더링할 이미지 수 (360도를 나누어 회전할 프레임 수)
radius = 10  # 카메라가 원점을 기준으로 떨어진 거리

# Blend 파일 열기
bpy.ops.wm.open_mainfile(filepath=blend_file_path)

# 카메라 가져오기 (기본 카메라가 있다고 가정)
camera = bpy.data.objects['Camera']

# 카메라 설정
camera.location = (0, -radius, 1)
camera.rotation_euler = (math.pi / 2, 0, 0)

# 원점에 빈 오브젝트 추가 (카메라의 회전 축)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
empty = bpy.context.active_object

# 카메라를 빈 오브젝트에 부모로 설정
camera.parent = empty

# 2D 렌더링 설정
bpy.context.scene.render.image_settings.file_format = 'PNG'


# 카메라 회전 및 렌더링
for i in range(num_frames):
    angle = (i / num_frames) * 2 * math.pi
    empty.rotation_euler[2] = angle
    output_file = f"{output_dir}/{i:03d}.png"
    bpy.context.scene.render.filepath = output_file
    bpy.ops.render.render(write_still=True)

print("Rendering completed successfully.")
