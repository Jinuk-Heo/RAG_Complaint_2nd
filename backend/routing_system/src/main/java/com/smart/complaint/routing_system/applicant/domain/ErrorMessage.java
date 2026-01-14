package com.smart.complaint.routing_system.applicant.domain;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum ErrorMessage {

    USER_DUPLICATE(404, "USER_DUPLICATE", "이미 존재하는 사용자입니다."),
    USER_NOT_FOUND(404, "USER_NOT_FOUND", "사용자를 찾을 수 없습니다."),
    COMPLAINT_NOT_FOUND(404, "COMPLAINT_NOT_FOUND", "민원을 찾을 수 없습니다"),
    INVALID_PASSWORD(400, "INVALID_PASSWORD", "비밀번호가 일치하지 않습니다."),
    INVALID_TOKEN(401, "INVALID_TOKEN", "유효하지 않은 토큰입니다."),
    EMAIL_SEND_FAILURE(454, "EMAIL_SEND_FAILURE", "이메일 전송에 실패했습니다."),    
    NOT_ALLOWED(400, "NOT_ALLOWED", "잘못된 요청입니다.");

    private final int status;
    private final String code;
    private final String message;
}