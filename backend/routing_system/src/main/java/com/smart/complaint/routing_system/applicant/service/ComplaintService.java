package com.smart.complaint.routing_system.applicant.service;

import com.smart.complaint.routing_system.applicant.dto.ComplaintAnswerRequest;
import com.smart.complaint.routing_system.applicant.dto.ComplaintRerouteRequest;
import com.smart.complaint.routing_system.applicant.entity.Complaint;
import com.smart.complaint.routing_system.applicant.entity.ComplaintReroute;
import com.smart.complaint.routing_system.applicant.repository.ComplaintRepository;
import com.smart.complaint.routing_system.applicant.repository.ComplaintRerouteRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class ComplaintService {

    private final ComplaintRepository complaintRepository;
    private final ComplaintRerouteRepository rerouteRepository;

    /**
     * 1. 담당자 배정 (Assign)
     * - 민원의 상태를 '처리중'으로 변경하고 담당자를 지정합니다.
     */
    public void assignManager(Long complaintId, Long userId) {
        Complaint complaint = complaintRepository.findById(complaintId)
                .orElseThrow(() -> new IllegalArgumentException("해당 민원을 찾을 수 없습니다. ID=" + complaintId));

        // (선택사항) 이미 다른 담당자가 있는지 체크하는 로직을 추가할 수 있습니다.
        // if (complaint.getAnsweredBy() != null && !complaint.getAnsweredBy().equals(userId)) { ... }

        complaint.assignManager(userId); // Entity의 편의 메서드 호출
    }

    /**
     * 2. 답변 저장/전송 (Answer)
     * - isTemporary=true: 답변 내용만 업데이트 (임시저장)
     * - isTemporary=false: 답변 내용 업데이트 + 상태 종결 + 답변일시 기록
     */
    public void saveAnswer(Long complaintId, ComplaintAnswerRequest request) {
        Complaint complaint = complaintRepository.findById(complaintId)
                .orElseThrow(() -> new IllegalArgumentException("해당 민원을 찾을 수 없습니다. ID=" + complaintId));

        if (request.isTemporary()) {
            // 임시 저장
            complaint.updateAnswerDraft(request.getAnswer());
        } else {
            // 답변 완료 및 종결 처리
            complaint.completeAnswer(request.getAnswer());
        }
    }

    /**
     * 3. 재이관 요청 (Reroute)
     * - 민원 테이블은 건드리지 않고, 재이관 이력 테이블에 요청 데이터를 쌓습니다.
     * - 관리자가 승인하기 전까지는 기존 부서/담당자가 유지됩니다.
     */
    public void requestReroute(Long complaintId, ComplaintRerouteRequest request, Long userId) {
        Complaint complaint = complaintRepository.findById(complaintId)
                .orElseThrow(() -> new IllegalArgumentException("해당 민원을 찾을 수 없습니다. ID=" + complaintId));

        // 재이관 요청 엔티티 생성
        ComplaintReroute reroute = ComplaintReroute.builder()
                .complaint(complaint)
                .originDepartmentId(complaint.getCurrentDepartmentId()) // 현재 부서
                .targetDepartmentId(request.getTargetDeptId())          // 희망 부서
                .requestReason(request.getReason())                     // 사유
                .requesterId(userId)                                    // 요청자 (나)
                .status("PENDING")                                      // 대기 상태
                .build();

        rerouteRepository.save(reroute);
    }
}