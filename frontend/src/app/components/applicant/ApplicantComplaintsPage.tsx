import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Complaint {
  id: string;
  title: string;
  category: string;
  content: string;
  status: 'received' | 'categorizing' | 'assigned' | 'answered' | 'closed';
  submittedDate: string;
  lastUpdate?: string;
  department?: string;
  assignedTo?: string;
}

interface PastComplaintsPageProps {
  complaints: Complaint[];
  onViewDetail: (complaintId: string) => void;
}

const STATUS_LABELS = {
  received: '접수됨',
  categorizing: '분류중',
  assigned: '담당자 배정',
  answered: '답변 완료',
  closed: '처리 완료',
};

const STATUS_COLORS = {
  received: 'bg-blue-100 text-blue-700 border-blue-300',
  categorizing: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  assigned: 'bg-purple-100 text-purple-700 border-purple-300',
  answered: 'bg-green-100 text-green-700 border-green-300',
  closed: 'bg-gray-100 text-gray-700 border-gray-300',
};

export default function ApplicantComplaintsPage({ onViewDetail }: PastComplaintsPageProps) {
  const navigate = useNavigate();

  const [complaints, setComplaints] = useState<Complaint[]>([]); // 내부 상태로 관리
  const [isLoading, setIsLoading] = useState(true); // 로딩 상태 추가
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const fetchComplaints = async () => {
      try {
        const response = await axios.get('/api/applicant/complaints'); // 실제 API 경로
        setComplaints(response.data);
      } catch (error) {
        console.error("데이터 로드 실패:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchComplaints();
  }, []);
  
  const itemsPerPage = 10;
  const handleGoHome = () => navigate('/applicant/main');

  // Calculate pagination
  const totalPages = Math.ceil(complaints.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentComplaints = complaints.slice(startIndex, endIndex);

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  return (
    <div className="min-h-screen bg-blue-50">
      {/* Top Navigation Bar */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-500 border-b border-blue-700 px-6 py-5 shadow-md">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">과거 민원 내역</h1>
            <Button
              onClick={handleGoHome}
              variant="outline"
              className="bg-white text-blue-600 border-white hover:bg-blue-50 hover:text-blue-700 h-11 px-6 text-base"
            >
              홈으로 돌아가기
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-400 px-6 py-4">
            <div className="flex items-center justify-between">
              <p className="text-white text-lg">
                총 <span className="font-bold text-xl">{complaints.length}</span>건의 민원
              </p>
              <p className="text-blue-100 text-sm">
                {currentPage} / {totalPages} 페이지
              </p>
            </div>
          </div>

          {/* Complaints List */}
          <div className="divide-y divide-gray-200">
            {currentComplaints.map((complaint) => (
              <div
                key={complaint.id}
                className="p-6 hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-3">
                    {/* Title and ID */}
                    <div className="flex items-start gap-3">
                      <span className="text-sm font-medium text-gray-500 mt-1">
                        {complaint.id}
                      </span>
                      <h3 className="text-xl font-semibold text-gray-900 flex-1">
                        {complaint.title}
                      </h3>
                    </div>

                    {/* Category and Status */}
                    <div className="flex items-center gap-3 flex-wrap">
                      <Badge className="bg-blue-100 text-blue-700 border border-blue-300 text-sm px-3 py-1">
                        {complaint.category}
                      </Badge>
                      <Badge className={`border text-sm px-3 py-1 ${STATUS_COLORS[complaint.status]}`}>
                        {STATUS_LABELS[complaint.status]}
                      </Badge>
                      {complaint.lastUpdate && (
                        <span className="text-sm text-red-600 font-medium">
                          🔔 업데이트됨
                        </span>
                      )}
                    </div>

                    {/* Content Preview */}
                    <p className="text-gray-600 text-base line-clamp-2">
                      {complaint.content}
                    </p>

                    {/* Meta Information */}
                    <div className="flex items-center gap-6 text-sm text-gray-500">
                      <span>제출일: {complaint.submittedDate}</span>
                      {complaint.lastUpdate && (
                        <span className="text-blue-600 font-medium">
                          최종 업데이트: {complaint.lastUpdate}
                        </span>
                      )}
                      {complaint.department && (
                        <span>담당부서: {complaint.department}</span>
                      )}
                    </div>
                  </div>

                  {/* View Detail Button */}
                  <Button
                    onClick={() => onViewDetail(complaint.id)}
                    className="bg-blue-600 hover:bg-blue-700 text-white h-11 px-6 flex items-center gap-2"
                  >
                    <Eye className="w-4 h-4" />
                    상세보기
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-gray-50 px-6 py-5 border-t border-gray-200">
              <div className="flex items-center justify-center gap-2">
                <Button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  variant="outline"
                  className="h-10 px-4"
                >
                  <ChevronLeft className="w-5 h-5" />
                </Button>

                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <Button
                      key={page}
                      onClick={() => goToPage(page)}
                      variant={currentPage === page ? 'default' : 'outline'}
                      className={`h-10 w-10 ${
                        currentPage === page
                          ? 'bg-blue-600 hover:bg-blue-700 text-white'
                          : 'hover:bg-blue-50'
                      }`}
                    >
                      {page}
                    </Button>
                  ))}
                </div>

                <Button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  variant="outline"
                  className="h-10 px-4"
                >
                  <ChevronRight className="w-5 h-5" />
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Empty State */}
        {complaints.length === 0 && (
          <div className="bg-white rounded-xl shadow-md p-12 text-center">
            <p className="text-gray-500 text-lg">제출한 민원이 없습니다.</p>
            <p className="text-gray-400 text-sm mt-2">새 민원을 작성해보세요.</p>
          </div>
        )}
      </main>
    </div>
  );
}
