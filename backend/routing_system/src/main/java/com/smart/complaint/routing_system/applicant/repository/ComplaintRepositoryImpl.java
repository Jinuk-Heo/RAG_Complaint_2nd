package com.smart.complaint.routing_system.applicant.repository;

import com.querydsl.core.types.OrderSpecifier;
import com.querydsl.core.types.Projections;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.core.types.dsl.Expressions;
import com.querydsl.core.types.dsl.NumberTemplate;
import com.querydsl.jpa.impl.JPAQueryFactory;
import com.smart.complaint.routing_system.applicant.domain.ComplaintStatus;
import com.smart.complaint.routing_system.applicant.domain.UrgencyLevel;
import com.smart.complaint.routing_system.applicant.dto.ComplaintDetailDto;
import com.smart.complaint.routing_system.applicant.dto.ComplaintDto;
import com.smart.complaint.routing_system.applicant.dto.ComplaintResponse;
import com.smart.complaint.routing_system.applicant.dto.ComplaintSearchCondition;
import com.smart.complaint.routing_system.applicant.dto.ComplaintSearchResult;
import com.smart.complaint.routing_system.applicant.entity.QComplaint;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.stream.Collectors;
import static com.smart.complaint.routing_system.applicant.entity.QComplaint.complaint;
import com.smart.complaint.routing_system.applicant.entity.QComplaintNormalization; // 팀원의 Q클래스
import org.springframework.util.StringUtils;

@Repository
@RequiredArgsConstructor
public class ComplaintRepositoryImpl implements ComplaintRepositoryCustom {

    private final JPAQueryFactory queryFactory;
    private final QComplaintNormalization normalization = QComplaintNormalization.complaintNormalization;

    @Override
    public List<ComplaintResponse> search(Long departmentId, ComplaintSearchCondition condition) {

        var results = queryFactory
                .selectFrom(complaint)
                .where(
                        // 1. 내 부서 ID와 일치하는 것만 (필수 보안)
                        complaint.currentDepartmentId.eq(departmentId),

                        // 2. 검색 필터들
                        keywordContains(condition.getKeyword()),
                        statusEq(condition.getStatus()),
                        hasIncident(condition.getHasIncident()))
                .orderBy(getOrderSpecifier(condition.getSort())) // 정렬 적용
                .fetch();

        return results.stream()
                .map(ComplaintResponse::new)
                .collect(Collectors.toList());
    }

    @Override
    public List<ComplaintSearchResult> findSimilarComplaint(double[] queryEmbedding, int limit) {
        String vectorString = java.util.Arrays.toString(queryEmbedding);

        // PGVector 코사인 거리 계산 (1 - Cosine Distance)
        NumberTemplate<Double> similarity = Expressions.numberTemplate(Double.class,
                "1 - ({0} <-> cast({1} as vector))",
                normalization.embedding,
                vectorString);

        return queryFactory
                .select(Projections.constructor(ComplaintSearchResult.class,
                        complaint.id,
                        complaint.title,
                        complaint.body,
                        similarity.as("score")))
                .from(normalization)
                .join(normalization.complaint, complaint)
                .where(normalization.isCurrent.isTrue())
                .orderBy(similarity.desc())
                .limit(limit)
                .fetch();
    }

    @Override
    public List<ComplaintDto> findTop3RecentComplaintByApplicantId(Long applicantId) {
        QComplaint complaint = QComplaint.complaint;

        return queryFactory
                .select(Projections.constructor(ComplaintDto.class,
                        complaint.id,
                        complaint.title,
                        complaint.status, // 엔티티의 Enum 타입
                        complaint.createdAt // 엔티티의 LocalDateTime 타입
                ))
                .from(complaint)
                .where(complaint.applicantId.eq(applicantId))
                .orderBy(complaint.createdAt.desc())
                .limit(3)
                .fetch();
    }

    @Override
    public List<ComplaintDetailDto> findAllByApplicantId(Long applicantId, String keyword) {
        QComplaint complaint = QComplaint.complaint;

        return queryFactory
                .select(Projections.constructor(ComplaintDetailDto.class,
                        complaint.id,
                        complaint.title,
                        complaint.body,
                        complaint.answer,
                        complaint.addressText,
                        complaint.status,
                        complaint.createdAt,
                        complaint.updatedAt
                // record의 생성자 파라미터 순서와 데이터 타입이 정확이 일치해야함
                ))
                .from(complaint)
                .where(
                        complaint.applicantId.eq(applicantId),
                        titleContains(keyword))
                .orderBy(complaint.createdAt.desc())
                .fetch();
    }

    // --- 조건 메서드 ---
    private BooleanExpression keywordContains(String keyword) {
        if (keyword == null || keyword.isEmpty())
            return null;
        return complaint.title.contains(keyword)
                .or(complaint.body.contains(keyword));
    }

    private BooleanExpression statusEq(ComplaintStatus status) {
        return status != null ? complaint.status.eq(status) : null;
    }

    private BooleanExpression hasIncident(Boolean hasIncident) {
        if (hasIncident == null)
            return null;
        return hasIncident ? complaint.incidentId.isNotNull() : complaint.incidentId.isNull();
    }

    private BooleanExpression titleContains(String keyword) {
        // 검색어가 없으면(null 또는 빈 문자열) null을 반환 -> where 절에서 무시됨
        return StringUtils.hasText(keyword) ? QComplaint.complaint.title.contains(keyword) : null;
    }

    // --- 정렬 메서드 (Sort) ---
    private OrderSpecifier<?> getOrderSpecifier(String sort) {
        if ("status".equals(sort)) {
            return complaint.status.asc();
        }
        // 기본값: 최신순
        return complaint.receivedAt.desc();
    }
}