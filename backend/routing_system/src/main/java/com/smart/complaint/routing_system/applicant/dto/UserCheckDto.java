package com.smart.complaint.routing_system.applicant.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

@Valid
public record UserCheckDto(
    @NotBlank
    @Size(min = 5, max = 15, message = "아이디는 5~15자의 영문 소문자와 숫자만 가능합니다.")
    @Pattern(regexp = "^[a-z0-9]{5,15}$")
    String userId,
    @NotBlank
    String email) {
}
