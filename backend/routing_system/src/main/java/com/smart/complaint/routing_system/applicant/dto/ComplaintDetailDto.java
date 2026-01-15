package com.smart.complaint.routing_system.applicant.dto;

import java.time.LocalDateTime;

import com.smart.complaint.routing_system.applicant.domain.ComplaintStatus;
import com.smart.complaint.routing_system.applicant.entity.Complaint;

public record ComplaintDetailDto(
        Long id,
        String title,
        String body,
        String answer,
        String addressText,
        ComplaintStatus status,
        LocalDateTime createdAt,
        LocalDateTime updatedAt) {
    public static ComplaintDetailDto from(Complaint entity) {
        return new ComplaintDetailDto(
                entity.getId(),
                entity.getTitle(),
                entity.getBody(),
                entity.getAnswer(),
                entity.getAddressText(),
                entity.getStatus(),
                entity.getCreatedAt(),
                entity.getUpdatedAt());
    }
}
