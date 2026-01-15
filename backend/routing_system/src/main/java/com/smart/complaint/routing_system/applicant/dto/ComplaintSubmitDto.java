package com.smart.complaint.routing_system.applicant.dto;

import java.math.BigDecimal;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class ComplaintSubmitDto {
    private String title; // 민원 제목
    private String body; // 민원 본문
    private String addressText; // 도로명 주소 (지도에서 변환된 값)

    // SQL의 DECIMAL(10,7)과 매핑되도록 BigDecimal 사용 권장
    private BigDecimal lat; // 위도
    private BigDecimal lon; // 경도

    // 추가로 필요한 정보들
    private Long applicantId; // 민원인 ID (Long)
    private Long districtId; // 발생 구역 ID
}
