package com.smart.complaint.routing_system.applicant.dto;

import lombok.Data;

@Data
public class ComplaintAnswerRequest {
    private String answer;       // 답변 내용
    private boolean isTemporary; // true: 임시저장, false: 종결
}