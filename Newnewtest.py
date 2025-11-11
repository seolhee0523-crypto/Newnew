import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

// ------------------------------------------
// 1. 사진 선택/촬영 및 업로드 처리 함수
// ------------------------------------------
Future<void> uploadAndVerifyCleanup(String studentName) async {
  final picker = ImagePicker();
  // 사용자가 사진을 선택/촬영
  final XFile? pickedFile = await picker.pickImage(source: ImageSource.camera); // 카메라 사용 예시

  if (pickedFile != null) {
    File imageFile = File(pickedFile.path);

    try {
      // 1. Firebase Storage에 이미지 업로드
      // 파일 이름: 'cleanup_photos/YYYYMMDD_HHmmss_StudentName.jpg' 형식
      String fileName = 'cleanup_photos/${DateTime.now().millisecondsSinceEpoch}_$studentName.jpg';
      Reference storageRef = FirebaseStorage.instance.ref().child(fileName);

      // 파일 업로드 실행
      UploadTask uploadTask = storageRef.putFile(imageFile);
      TaskSnapshot snapshot = await uploadTask;

      // 업로드된 이미지의 다운로드 URL 획득
      String downloadURL = await snapshot.ref.getDownloadURL();

      // 2. Firebase Firestore에 인증 정보 저장
      await FirebaseFirestore.instance.collection('cleanup_verifications').add({
        'student_name': studentName,
        'image_url': downloadURL,
        'timestamp': FieldValue.serverTimestamp(), // 서버 시간으로 저장
        'is_verified': false, // 선생님이 나중에 확인할 수 있는 필드
      });

      print("청소 인증 성공: $downloadURL");
      // TODO: 사용자에게 성공 메시지 표시 (예: ScaffoldMessenger)

    } catch (e) {
      print("청소 인증 중 오류 발생: $e");
      // TODO: 사용자에게 오류 메시지 표시
    }
  } else {
    print('사진 선택이 취소되었습니다.');
  }
}

// ------------------------------------------
// 2. 사용 예시 (Flutter 위젯)
// ------------------------------------------
class CleanupVerificationButton extends StatelessWidget {
  final String currentStudentName = '김철수'; // 실제 앱에서는 로그인된 사용자 이름 사용

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () => uploadAndVerifyCleanup(currentStudentName),
      child: const Text('🧹 청소 인증샷 올리기'),
    );
  }
}
