package com.smart.complaint.routing_system.applicant.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class LoginResponseDto {

    @Schema(description = "JWT")
    private String token;    // 추후 JWT
    private String username;
    private String role;     // 프론트엔드가 화면을 나눌 기준 (ADMIN / AGENT)
}