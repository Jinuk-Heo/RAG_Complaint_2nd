package com.smart.complaint.routing_system.applicant.dto;

import java.math.BigDecimal;

import com.smart.complaint.routing_system.applicant.entity.Complaint;

public record ComplaintHeatMap(
        Long id,
        BigDecimal lat,
        BigDecimal lon) {
    public static ComplaintHeatMap from(Complaint entity) {
        // null 방어 로직 추가
        if (entity.getLat() == null || entity.getLon() == null) {
            return null;
        }
        return new ComplaintHeatMap(
                entity.getId(),
                entity.getLat(),
                entity.getLon());
    }
}
