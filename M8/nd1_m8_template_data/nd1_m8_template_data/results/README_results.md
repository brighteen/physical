# results 폴더 — 실행 시 자동 생성되는 산출물

## 저장되는 파일 목록

| 파일 | 생성 방법 | 제출 여부 |
|------|---------|---------|
| M8_cp1_odom_log.png | CP1 실행 로그 스크린샷 | ✅ 필수 |
| M8_cp2_map.pgm | ~/map/에서 복사 | ✅ 필수 |
| M8_cp2_coverage_sim.png | 01_quickstart.ipynb 실행 | 권장 |
| M8_cp3_goals.png | 01_quickstart.ipynb 실행 | 권장 |
| M8_cp3_success_log.png | CP3 완료 로그 스크린샷 | ✅ 필수 |
| M8_cp1_shimhwa_rviz.png | CP1 심화 RViz2 + 터미널 로그 | 가산점 +4 |
| M8_system_diagram.png | 시스템 구성도 (선택) | 권장 |

## 스크린샷 가이드

### CP1 필수 스크린샷
- `ros2 topic hz /cmd_vel` 결과 (average rate ≥ 2.0 포함)
- 터미널 로그 (`[CP1] 위치: x=..., y=...` 포함)

### CP1 심화 스크린샷 (가산점 +4)
- RViz2 화면: `/obstacle_markers` 빨간 구(Sphere) 시각화
- 터미널 로그: `[CP1 심화] 유효 포인트: N/360` 포함
- 두 화면을 나란히 캡처하는 것 권장

### CP2 필수 스크린샷
- `[CP2] ✅ 커버리지 목표 달성` WARN 로그
- `ls -lh ~/map/` 결과 (my_map.yaml, my_map.pgm 포함)

### CP3 필수 스크린샷
- `[INFO] 목표 1/2/3 도달 완료!` 로그 3줄 연속
- `[CP3] ★ 모든 목표 완료!` 마지막 로그

## 제출 체크리스트

- [ ] CP1 스크린샷 (cmd_vel hz + odom 로그)
- [ ] CP2 지도 파일 (yaml + pgm)
- [ ] CP3 완료 로그 스크린샷
- [ ] CP1 심화 스크린샷 (RViz2 obstacle_markers + [CP1 심화] 로그)
- [ ] README.md 데모 영상 링크 업데이트
