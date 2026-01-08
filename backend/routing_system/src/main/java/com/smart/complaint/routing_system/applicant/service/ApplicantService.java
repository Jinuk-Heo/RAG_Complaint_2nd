package com.smart.complaint.routing_system.applicant.service;

import java.util.List;

import com.smart.complaint.routing_system.applicant.repository.ComplaintRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import com.smart.complaint.routing_system.applicant.dto.ComplaintDto;

// 민원인 서비스
@Service
@RequiredArgsConstructor
public class ApplicantService {

    private final ComplaintRepository complaintRepository;

    public List<ComplaintDto> getAllComplaints(String applicantId) {

        complaintRepository.find

        return null;
    }
}
