package com.smart.complaint.routing_system.applicant.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
public class AdminLoginRequestDto {
    @Schema(description = "내부자 아이디", example = "admin")
    private String username;

    @Schema(description = "비밀번호", example = "1234")
    private String password;
}