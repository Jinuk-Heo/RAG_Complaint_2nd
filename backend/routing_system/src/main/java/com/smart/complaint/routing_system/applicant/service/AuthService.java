package com.smart.complaint.routing_system.applicant.service;

import com.smart.complaint.routing_system.applicant.config.LoginFailedException;
import com.smart.complaint.routing_system.applicant.dto.LoginResponseDto;
import com.smart.complaint.routing_system.applicant.entitiy.User;
import org.springframework.stereotype.Service;

import com.smart.complaint.routing_system.applicant.domain.UserRole;
import com.smart.complaint.routing_system.applicant.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder; // SecurityConfig에서 등록한 녀석

    public LoginResponseDto internalLogin(String username, String rawPassword) {
        // 아이디로 유저 찾기
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 사용자입니다."));

        // 역할 검증 (시민은 이 로직으로 로그인불가)
        if (user.getRole() == UserRole.CITIZEN) {
            throw new IllegalArgumentException("내부 직원 전용 페이지입니다.");
        }

//        System.out.println("=== 디버깅 로그 시작 ===");
//        System.out.println("1. 사용자가 입력한 비번: [" + rawPassword + "]");
//        System.out.println("2. DB에서 가져온 해시값: [" + user.getPassword() + "]");
//        System.out.println("3. 검증 결과: " + passwordEncoder.matches(rawPassword, user.getPassword()));
//        System.out.println("=== 디버깅 로그 끝 ===");

        // 비밀번호 검증 ( matches 함수 사용)
        // rawPassword: 사용자가 입력한 "1234"
        // user.getPassword(): DB에 있는 "$2a$10$Rx..."
        if (!passwordEncoder.matches(rawPassword, user.getPassword())) {
            throw new LoginFailedException("로그인 정보가 일치하지 않습니다.");
        }

        // 성공 시 응답 (나중에 role에 따라 프론트가 화면 분기)
        return new LoginResponseDto(
                "dummy-token-abcde",
                user.getUsername(),
                user.getRole().name()
        );
    }

    /**
     * [추가] 공무원 로그인용: 비밀번호 검사 후 User 엔티티 원본 반환
     */
    public User authenticate(String username, String password) {
        // 아이디 조회
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new LoginFailedException("로그인 정보가 일치하지 않습니다."));

        // 비밀번호 대조
        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new LoginFailedException("로그인 정보가 일치하지 않습니다.");
        }

        // User 엔티티 그대로 반환
        return user;
    }
}