package com.smart.complaint.routing_system.applicant.controller; // ★ 본인 패키지 위치에 맞게 수정하세요!

import com.smart.complaint.routing_system.applicant.dto.AdminLoginRequestDto;
import com.smart.complaint.routing_system.applicant.entitiy.User;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import com.smart.complaint.routing_system.applicant.service.AuthService;
import com.smart.complaint.routing_system.applicant.domain.UserRole;

@RestController
@RequestMapping("/api/agent") // 공무원 전용 주소
@RequiredArgsConstructor
public class AgentController {

    private final AuthService authService;

    /**
     * 공무원 전용 로그인 (세션 방식)
     * POST /api/agent/login
     */
    @PostMapping("/login")
    public ResponseEntity<?> agentLogin(@RequestBody AdminLoginRequestDto request, HttpServletRequest httpRequest) {

        // 아이디/비번 검증 (AuthService가 DB 확인하고 비번 대조함)
        // (DTO에 getUsername, getPassword가 있어야 함)
        User user = authService.authenticate(request.getUsername(), request.getPassword());

        // 공무원(AGENT) 아니면 쫓아냄 (이중 보안)
        if (user.getRole() != UserRole.AGENT && user.getRole() != UserRole.ADMIN) {
            throw new IllegalArgumentException("접근 권한이 없습니다.");
        }

        // 세션(Session) 생성 및 저장
        // getSession(true): 세션이 없으면 새로 만들고, 있으면 그거 가져옴
        HttpSession session = httpRequest.getSession(true);

        // 세션에 "LOGIN_USER"라는 이름으로 유저 정보(객체)를 통째로 저장
        session.setAttribute("LOGIN_USER", user);

        // 세션 유지 시간 설정 (초 단위) -> 1800초 = 30분
        // 30분 동안 아무런 요청 없으면 자동으로 로그아웃됨 (보안 필수 요건)
        session.setMaxInactiveInterval(1800);

        // 응답 (토큰 안 줌 그냥 성공 메시지만 줌)
        return ResponseEntity.ok()
                .body("공무원 로그인 성공! (세션 ID가 쿠키로 발급되었습니다)");
    }

    /**
     * 로그아웃 기능 (세션 날리기)
     * POST /api/agent/logout
     */
    @PostMapping("/logout")
    public ResponseEntity<?> agentLogout(HttpServletRequest httpRequest) {
        HttpSession session = httpRequest.getSession(false);
        if (session != null) {
            session.invalidate(); // 세션 삭제 (서버 메모리에서 삭제)
        }
        return ResponseEntity.ok("로그아웃 되었습니다.");
    }
}