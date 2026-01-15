import { useEffect, useState } from 'react';
import { Toolbar } from './toolbar';
import { RecentComplaints } from './recent-complaints';
import { ResponseTimeStats } from './response-time-stats';
import { KeywordCloud } from './keyword-cloud';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Swal from 'sweetalert2';

interface ComplaintDto {
  id: number;
  title: string;
  complaintStatus: string; // status -> complaintStatus
  createdAt: string;       // submittedDate -> createdAt
}

// Mock data for response time statistics
const mockResponseTimeData = [
  { category: '도로/교통', avgDays: 3.2 },
  { category: '환경/위생', avgDays: 5.1 },
  { category: '공원/시설', avgDays: 4.5 },
  { category: '안전/치안', avgDays: 2.8 },
  { category: '기타', avgDays: 6.3 },
];

const mockOverallStats = {
  averageResponseTime: 4.4,
  fastestCategory: '안전/치안',
  improvementRate: 12,
};

// Mock data for keywords
const mockKeywords = [
  { text: '가로등', value: 45 },
  { text: '주정차', value: 38 },
  { text: '포트홀', value: 32 },
  { text: '쓰레기', value: 28 },
  { text: '소음', value: 25 },
  { text: '교통', value: 22 },
  { text: '안전', value: 20 },
  { text: '보수', value: 18 },
  { text: '보도', value: 15 },
  { text: '공원', value: 12 },
  { text: '하수구', value: 10 },
  { text: '가로수', value: 8 },
  { text: '공사', value: 7 },
  { text: '불법', value: 6 },
];

const ApplicantMainPage = () => {

  const navigate = useNavigate();

  const handleViewComplaints = () => {
    console.log('과거 민원 보기');
    navigate('/applicant/complaints');
    // Navigate to complaints list view
  };

  const handleNewComplaint = () => {
    console.log('새 민원 작성');
    navigate('/applicant/complaints/new');
    // Navigate to new complaint form
  };

  const handleLogout = () => {
    Swal.fire({
      title: '로그아웃',
      text: "정말 로그아웃 하시겠습니까?",
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: '로그아웃',
      cancelButtonText: '취소'
    }).then((result) => {
      if (result.isConfirmed) {
        localStorage.removeItem('accessToken');
        Swal.fire(
          '로그아웃 완료',
          '성공적으로 로그아웃되었습니다.',
          'success'
        ).then(() => {
          navigate('/applicant/login');
        });
      }
    });
  };

  const [recentComplaints, setRecentComplaints] = useState<ComplaintDto[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {

    const token = localStorage.getItem('accessToken');
    if (!token) {
      Swal.fire({
        title: '로그인 필요',
        text: '민원 서비스를 이용하기 위해서는 로그인이 필요합니다!',
        icon: 'warning',
        confirmButtonText: '로그인 하러 가기'
      }).then((result) => {
        if (result.isConfirmed) {
          navigate('/applicant/login');
        }
      });
      return;
    }

    const fetchRecentComplaints = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        // 백엔드 API 호출 - 최근 3개의 민원 불러오기
        // 백엔드에서 만든 최신 3개 전용 API 호출
        const response = await axios.get('http://localhost:8080/api/applicant/complaints/top3', {
          headers: { Authorization: `Bearer ${token}` }
        });

        setRecentComplaints(response.data);
      } catch (error) {
        console.error("최신 민원 로드 실패:", error);
      } finally {
        setIsLoading(false);
      }

    };
    fetchRecentComplaints();
    // 빈 배열: 한 번만 실행, accessToken: 변경 시 재실행
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Toolbar
        onViewComplaints={handleViewComplaints}
        onNewComplaint={handleNewComplaint}
        onLogout={handleLogout}
      />

      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* 메인 그리드 컨테이너: 좌(2) : 우(3) 비율 */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 items-start">

          {/* [좌측 섹션] 최근 민원 TOP 3 - col-span-2 (40%) */}
          <section className="lg:col-span-2 bg-white rounded-[32px] border border-gray-100 shadow-sm overflow-hidden h-full">
            <div className="p-8 space-y-8">
              {/* Section Header */}
              <div className="flex justify-between items-center border-b border-gray-50 pb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <span className="text-xl">📋</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-800">최근 민원 현황</h3>
                    <p className="text-xs text-gray-400">최근 접수된 3건입니다.</p>
                  </div>
                </div>
                <span className="px-3 py-1 bg-blue-600 text-white text-[10px] font-bold rounded-full shadow-sm">
                  TOP 3
                </span>
              </div>

              {/* Complaints Vertical List */}
              <div className="flex flex-col gap-4">
                {isLoading ? (
                  <div className="flex justify-center py-20">
                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
                  </div>
                ) : Array.isArray(recentComplaints) && recentComplaints.length > 0 ? (
                  <>
                    {/* 실제 민원 카드 리스트 */}
                    {recentComplaints.map((complaint) => (
                      <div
                        key={complaint.id}
                        className="bg-white p-5 rounded-2xl border border-gray-100 hover:shadow-md transition-all cursor-pointer group"
                        onClick={() => navigate(`/applicant/complaints/${complaint.id}`)}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${complaint.complaintStatus === 'ANSWERED' ? 'bg-green-100 text-green-700' :
                              complaint.complaintStatus === 'ASSIGNED' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'
                            }`}>
                            {complaint.complaintStatus}
                          </span>
                          <span className="text-[11px] text-gray-400 font-medium">
                            {new Date(complaint.createdAt).toLocaleDateString()}
                          </span>
                        </div>
                        <h4 className="text-md font-bold text-gray-800 mb-1 group-hover:text-blue-600 transition-colors line-clamp-1">
                          {complaint.title}
                        </h4>
                        <p className="text-xs text-gray-400">상세 내용 보기 →</p>
                      </div>
                    ))}

                    {/* 3건 미만일 때 채워주는 Placeholder */}
                    {recentComplaints.length < 3 && (
                      [...Array(3 - recentComplaints.length)].map((_, index) => (
                        <div
                          key={`empty-${index}`}
                          onClick={handleNewComplaint}
                          className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer hover:bg-gray-100 hover:border-blue-300 transition-all group h-[120px]"
                        >
                          <span className="text-xl mb-1 group-hover:scale-110 transition-transform">➕</span>
                          <p className="text-xs font-semibold text-gray-400 group-hover:text-blue-600">새 민원 추가</p>
                        </div>
                      ))
                    )}
                  </>
                ) : (
                  /* 아예 민원이 없을 때 */
                  <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl py-20 flex flex-col items-center justify-center">
                    <span className="text-4xl mb-4">📄</span>
                    <h3 className="text-md font-bold text-gray-700">신청한 민원이 없습니다</h3>
                    <button onClick={handleNewComplaint} className="mt-4 text-sm text-blue-600 font-semibold hover:underline">+ 새 민원 작성</button>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* [우측 섹션] 통계 및 키워드 - col-span-3 (60%) */}
          <div className="lg:col-span-3 flex flex-col gap-8">

            {/* 우측 상단: 지역 민원 처리 현황 */}
            <section className="bg-white rounded-[32px] border border-gray-100 shadow-sm overflow-hidden p-2">
              <div className="p-6">
                <div className="flex items-center gap-2 mb-6 px-4">
                  <span className="text-lg">📊</span>
                  <h3 className="text-lg font-bold text-gray-800">지역 민원 처리 현황</h3>
                </div>
                <ResponseTimeStats
                  data={mockResponseTimeData}
                  overallStats={mockOverallStats}
                />
              </div>
            </section>

            {/* 우측 하단: 민원 키워드 분석 */}
            <section className="bg-white rounded-[32px] border border-gray-100 shadow-sm overflow-hidden p-2">
              <div className="p-6">
                <div className="flex items-center gap-2 mb-6 px-4">
                  <span className="text-lg">🔍</span>
                  <h3 className="text-lg font-bold text-gray-800">실시간 민원 키워드</h3>
                </div>
                <KeywordCloud keywords={mockKeywords} />
              </div>
            </section>

          </div>
        </div>
      </main>
    </div>
  );
}

export default ApplicantMainPage;