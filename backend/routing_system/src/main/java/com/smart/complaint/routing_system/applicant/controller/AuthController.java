package com.smart.complaint.routing_system.applicant.controller;

import com.smart.complaint.routing_system.applicant.dto.AdminLoginRequestDto;
import com.smart.complaint.routing_system.applicant.dto.LoginResponseDto;
import com.smart.complaint.routing_system.applicant.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Tag(name = "Auth API", description = "인증 관련 API")
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:3000")
public class AuthController {

    private final AuthService authService;

    @Operation(summary = "내부자 로그인", description = "관리자(ADMIN) 및 공무원(AGENT) 로그인")
    @PostMapping("/internal/login")
    public ResponseEntity<LoginResponseDto> login(@RequestBody AdminLoginRequestDto request) {
        LoginResponseDto response = authService.internalLogin(request.getUsername(), request.getPassword());
        return ResponseEntity.ok(response);
    }
}