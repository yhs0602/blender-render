# Blender Render Test

## 기본 설정
- 800 x 800
- 위쪽 그림 10장
- 중간 그림 60장
- 아래쪽 그림 10장
- 테스트이미지: 4 + 4 + 2장

## 찬장 그리기
- 각도 한정
- 가우시안 샘플링 테스트
```
blender --background /Users/yanghyeonseo/Downloads/shelf.blend --python render_shelf.py
```

## 식판 그리기
- 각도 360도
- 유니폼 샘플링 테스트
```shell
blender --background /Users/yanghyeonseo/Downloads/diningcar.blend --python render_sikpan.py
```

## 원숭이 컵 그리기
- 각도 360도
- 유니폼 샘플링 테스트
```shell
blender --background /Users/yanghyeonseo/Downloads/cup.blend --python render_monkey.py
```
## 콘센트 그리기
```shell
blender --background /Users/yanghyeonseo/Downloads/plug.blend --python render_outlet.py
```