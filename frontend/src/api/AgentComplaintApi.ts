import { springApi } from "../lib/springApi";

export type ComplaintStatus = 'RECEIVED' | 'RECOMMENDED' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED' | 'CANCLED';
export type UrgencyLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type IncidentStatus = 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';

// 목록 조회용 DTO
export interface ComplaintDto {
  id: number;
  title: string;
  body: string;
  addressText?: string;
  status: ComplaintStatus;
  urgency: UrgencyLevel;
  receivedAt: string;
  createdAt: string;
  updatedAt?: string;
  districtId?: number;
  incidentId?: string | null;
  category?: string;
  tags?: string[];
  neutralSummary?: string;
  managerName?: string;
}

// 상세 조회용 DTO (백엔드 ComplaintDetailResponse와 매핑)
export interface ComplaintDetailDto {
  // 기본 정보
  id: string;          // 화면 표시용 ID (예: C2026-0004)
  originalId: number;  // 실제 DB ID
  title: string;
  body: string;        // 원문 내용
  address: string;
  receivedAt: string;
  status: ComplaintStatus;
  urgency: UrgencyLevel;
  departmentName?: string; // 담당 부서
  category?: string;       // 업무군

  // 정규화 정보
  neutralSummary?: string;
  coreRequest?: string;
  coreCause?: string;
  targetObject?: string;
  keywords?: string[];
  locationHint?: string;

  // 사건 정보
  incidentId?: string;       // 화면 표시용 ID (예: I-2026-001)
  incidentTitle?: string;
  incidentStatus?: IncidentStatus;
  incidentComplaintCount?: number;

  // 상세 페이지 기능용 필드
  answeredBy?: number;   // 담당자 ID (권한 체크용)
  managerName?: string;  // 담당자 이름
  answer?: string;       // 답변 내용
}

// ID 파싱
const parseId = (id: string | number): number => {
  const idStr = String(id);
  // "C2026-0008" 형태라면 "-" 뒤의 숫자만 추출
  if (idStr.includes('-')) {
    return Number(idStr.split('-').pop());
  }
  return Number(idStr);
};

export const AgentComplaintApi = {

  // 0. 내 정보 가져오기
  getMe: async () => {
    const response = await springApi.get<{id: number, displayName: string}>("/api/agent/me");
    return response.data;
  },

  // 1. [목록] 모든 민원 가져오기
  getAll: async (params?: any) => {
    const response = await springApi.get<ComplaintDto[]>("/api/agent/complaints", { params });
    return response.data;
  },

  // 2. [상세] 특정 민원 1개 가져오기
  getDetail: async (id: string | number) => {
    const realId = parseId(id);
    const response = await springApi.get<ComplaintDetailDto>(`/api/agent/complaints/${realId}`);
    return response.data;
  },

  // 3. 담당 배정 (Assign)
  assign: async (id: string | number) => {
    const realId = parseId(id); // ★ 여기서 변환!
    await springApi.post(`/api/agent/complaints/${realId}/assign`);
  },

  // 4. 담당 취소 (Release)
  release: async (id: string | number) => {
    const realId = parseId(id); // ★ 여기서 변환!
    await springApi.post(`/api/agent/complaints/${realId}/release`);
  },

  // 5. 답변 전송/저장 (Answer)
  answer: async (id: string | number, content: string, isTemporary: boolean) => {
    const realId = parseId(id); // ★ 여기서 변환!
    await springApi.post(`/api/agent/complaints/${realId}/answer`, {
      answer: content,
      isTemporary,
    });
  },

  // 6. 재이관 요청 (Reroute)
  reroute: async (id: string | number, targetDeptId: number, reason: string) => {
    const realId = parseId(id); // ★ 여기서 변환!
    await springApi.post(`/api/agent/complaints/${realId}/reroute`, {
      targetDeptId,
      reason,
    });
  },
};