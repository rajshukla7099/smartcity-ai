@echo off
title SC-01: Video Motion Tracker (Video Mode)
echo =========================================================================================
echo  TRACK 05: SMART CITIES - SC-01: MULTI-CAMERA VEHICLE VIDEO TRACKER
echo  Dense Mixed Indian Traffic Localization & Tracking Without Reading Plates
echo =========================================================================================
python video_detector.py %*
pause
