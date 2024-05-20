import json
import math
import pathlib
import random

import bpy
import mathutils


# Sikpan: 360도, 테스트셋 유니폼 샘플링
# Monkey: 360도, 테스트셋 유니폼 샘플링?
# Shelf: 21, 33 사이만 돌아감. 테스트셋 가우스 샘플링

# Total: 10 60 10
# Up: 2 * 2
# Middle: 2 * 2
# Down: 1 * 2


# function from https://github.com/panmari/stanford-shapenet-renderer/blob/master/render_blender.py
def get_3x4_RT_matrix_from_blender(cam):
    # bcam stands for blender camera
    # R_bcam2cv = Matrix(
    #     ((1, 0,  0),
    #     (0, 1, 0),
    #     (0, 0, 1)))

    # Transpose since the rotation is object rotation,
    # and we want coordinate rotation
    # R_world2bcam = cam.rotation_euler.to_matrix().transposed()
    # T_world2bcam = -1*R_world2bcam @ location
    #
    # Use matrix_world instead to account for all constraints
    location, rotation = cam.matrix_world.decompose()[0:2]
    R_world2bcam = rotation.to_matrix().transposed()

    # Convert camera location to translation vector used in coordinate changes
    # T_world2bcam = -1*R_world2bcam @ cam.location
    # Use location from matrix_world to account for constraints:
    T_world2bcam = -1 * R_world2bcam @ location

    # # Build the coordinate transform matrix from world to computer vision camera
    # R_world2cv = R_bcam2cv@R_world2bcam
    # T_world2cv = R_bcam2cv@T_world2bcam

    # put into 3x4 matrix
    RT = mathutils.Matrix(
        (
            R_world2bcam[0][:] + (T_world2bcam[0],),
            R_world2bcam[1][:] + (T_world2bcam[1],),
            R_world2bcam[2][:] + (T_world2bcam[2],),
        )
    )
    return RT


def capture_images(
    empty,
    camera,
    output_dir,
    frames,
    num_frames,
    start_frame,
    end_frame,
    num_images,
    global_i: int,
    z_offset=0.0,
    random_sampling=False,
):
    angles = []
    if random_sampling:
        for _ in range(num_images):
            angle = random.uniform(start_frame, end_frame) * 360 / 36
            angles.append(math.radians(angle))

    else:
        angles = [
            (start_frame + (i / num_images) * (end_frame - start_frame))
            / num_frames
            * 2
            * math.pi
            for i in range(num_images)
        ]

    for i, angle in enumerate(angles):
        empty.rotation_euler[2] = angle
        camera.location.z = 1 + z_offset  # z_offset을 적용하여 카메라 높이 조정
        output_file = f"{output_dir}/{(global_i + i):03d}.png"
        output_relative_path = f"{output_dir.name}/{(global_i + i):03d}.png"
        bpy.context.scene.render.filepath = output_file
        bpy.ops.render.render(write_still=True)
        pos, rt, scale = camera.matrix_world.decompose()

        rt = rt.to_matrix()

        matrix = []
        for ii in range(3):
            a = []
            for jj in range(3):
                a.append(rt[ii][jj])
            a.append(pos[ii])
            matrix.append(a)
        matrix.append([0, 0, 0, 1])
        # print(matrix)

        to_add = {"file_path": output_relative_path, "transform_matrix": matrix}
        frames.append(to_add)
    return global_i + num_images


def main():
    # 설정 값
    current_dir = pathlib.Path(__file__).parent.absolute()
    output_dir = current_dir / "output"
    # blend_file_path = input_file
    train_output_dir = output_dir / "train"
    test_output_dir = output_dir / "test"
    camera_info_path = output_dir / "camera_info.json"
    if not output_dir.exists():
        output_dir.mkdir()
    if not train_output_dir.exists():
        train_output_dir.mkdir()
    if not test_output_dir.exists():
        test_output_dir.mkdir()

    num_frames = 36  # 렌더링할 이미지 수 (360도를 나누어 회전할 프레임 수)
    radius = 6  # 카메라가 원점을 기준으로 떨어진 거리

    # Blend 파일 열기
    # bpy.ops.wm.open_mainfile(filepath=blend_file_path)

    # 카메라 가져오기 (기본 카메라가 있다고 가정)
    camera = bpy.data.objects["Camera"]

    # 카메라 설정
    camera.location = (0, -radius, 1)
    camera.rotation_euler = (math.pi / 2, 0, 0)

    # 원점에 빈 오브젝트 추가 (카메라의 회전 축)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    empty = bpy.context.active_object

    # 카메라를 빈 오브젝트에 부모로 설정
    camera.parent = empty

    # 카메라가 항상 원점을 바라보도록 설정
    track_to_constraint = camera.constraints.new(type="TRACK_TO")
    track_to_constraint.target = empty
    track_to_constraint.track_axis = "TRACK_NEGATIVE_Z"
    track_to_constraint.up_axis = "UP_Y"

    # 2D 렌더링 설정
    image_width = 800
    image_height = 800
    # 흰색 설정
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (
        1,
        1,
        1,
        1,
    )  # 흰색 RGBA
    bpy.context.scene.display_settings.display_device = "sRGB"
    bpy.context.scene.view_settings.view_transform = "Standard"
    bpy.context.scene.view_settings.look = "None"
    bpy.context.scene.view_settings.exposure = 0.0
    bpy.context.scene.view_settings.gamma = 1.0

    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.resolution_x = image_width
    bpy.context.scene.render.resolution_y = image_height
    bpy.context.scene.render.resolution_percentage = 100  # 해상도 퍼센티지

    if False:
        train_transforms_json = {
            "camera_angle_x": bpy.data.cameras[0].angle_x,
        }
        train_frames = []
        global_i = 0
        global_i = capture_images(
            empty,
            camera,
            train_output_dir,
            train_frames,
            num_frames,
            0,  # 21
            35,  # 33
            60,
            global_i,
            z_offset=-0.75,
        )

        global_i = capture_images(
            empty,
            camera,
            train_output_dir,
            train_frames,
            num_frames,
            0,  # 21
            35,  # 33
            10,
            global_i,
            z_offset=0.3,
        )

        global_i = capture_images(
            empty,
            camera,
            train_output_dir,
            train_frames,
            num_frames,
            0,  # 21
            35,  # 33
            10,
            global_i,
            z_offset=-1.75,
        )

        train_transforms_json["frames"] = train_frames

        with open(output_dir / "transforms_train.json", "w") as f:
            json.dump(train_transforms_json, f, indent=4)

    # Test set capture
    test_frames = []
    global_i = 0
    global_i = capture_images(
        empty,
        camera,
        test_output_dir,
        test_frames,
        num_frames,
        8,  # 21 0 10 ~25
        13,  # 33 35 40~52
        2,
        global_i,
        z_offset=0.3,
        random_sampling=True,
    )

    global_i = capture_images(
        empty,
        camera,
        test_output_dir,
        test_frames,
        num_frames,
        25,  # 21 0 10 ~25
        30,  # 33 35 40~52
        2,
        global_i,
        z_offset=0.3,
        random_sampling=True,
    )

    global_i = capture_images(
        empty,
        camera,
        test_output_dir,
        test_frames,
        num_frames,
        8,  # 21
        13,  # 33
        1,
        global_i,
        z_offset=-1.75,
        random_sampling=True,
    )

    global_i = capture_images(
        empty,
        camera,
        test_output_dir,
        test_frames,
        num_frames,
        25,  # 21
        30,  # 33
        1,
        global_i,
        z_offset=-1.75,
        random_sampling=True,
    )

    global_i = capture_images(
        empty,
        camera,
        test_output_dir,
        test_frames,
        num_frames,
        8,  # 21
        13,  # 33
        2,
        global_i,
        z_offset=-0.75,
        random_sampling=True,
    )

    global_i = capture_images(
        empty,
        camera,
        test_output_dir,
        test_frames,
        num_frames,
        25,  # 21
        30,  # 33
        2,
        global_i,
        z_offset=-0.75,
        random_sampling=True,
    )

    test_transforms_json = {
        "camera_angle_x": bpy.data.cameras[0].angle_x,
        "frames": test_frames,
    }

    with open(output_dir / "transforms_test.json", "w") as f:
        json.dump(test_transforms_json, f, indent=4)

    print("Rendering completed successfully.")


if __name__ == "__main__":
    main()
