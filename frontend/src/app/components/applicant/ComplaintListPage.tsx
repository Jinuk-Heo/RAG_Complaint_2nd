import { useState, useMemo, useEffect, } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { ChevronLeft, ChevronRight, Eye, Search, Calendar, ArrowUpDown } from 'lucide-react';
import api from './AxiosInterface';
import { useNavigate } from 'react-router-dom';

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
  onGoHome: () => void;
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

type SortOption = 'date-desc' | 'date-asc' | 'status' | 'title';

const SORT_LABELS: Record<SortOption, string> = {
  'date-desc': '최신순',
  'date-asc': '오래된순',
  'status': '상태별',
  'title': '제목순',
};

export default function PastComplaintsPage() {
  const navigate = useNavigate();

  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [currentPage, setCurrentPage] = useState(1);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('date-desc');
  const [showSortMenu, setShowSortMenu] = useState(false);
  const itemsPerPage = 10;

  const handleViewDetail = (id: string) => {
    navigate(`/applicant/complaints/${id}`);
  };

  // 2. API 호출 로직
  useEffect(() => {
    const fetchComplaints = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('http://localhost:8080/api/applicant/complaints');

        // 백엔드 데이터(Entity)를 프론트엔드 인터페이스(Complaint)로 변환
        const formattedData = response.data.map((item: any) => ({
          id: item.id.toString(),
          title: item.title,
          category: item.category || '미분류', // 엔티티에 카테고리가 없다면 기본값
          content: item.body, // DB의 body 필드를 content로 매핑
          status: item.status.toLowerCase(), // RECEIVED -> received
          submittedDate: item.createdAt.split('T')[0], // 2026-01-14T... -> 2026-01-14
          department: item.departmentName, // 부서명이 있다면 매핑
        }));

        setComplaints(formattedData);
      } catch (error) {
        console.error("데이터 로드 실패:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchComplaints();
  }, []);

  // Filter and sort complaints
  const filteredAndSortedComplaints = useMemo(() => {
    let filtered = [...complaints];

    // Filter by keyword (search in title, content, category, id)
    if (searchKeyword.trim()) {
      const keyword = searchKeyword.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.title.toLowerCase().includes(keyword) ||
          c.content.toLowerCase().includes(keyword) ||
          c.category.toLowerCase().includes(keyword) ||
          c.id.toLowerCase().includes(keyword)
      );
    }

    // Filter by date range
    if (startDate) {
      filtered = filtered.filter((c) => c.submittedDate >= startDate);
    }
    if (endDate) {
      filtered = filtered.filter((c) => c.submittedDate <= endDate);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date-desc':
          return b.submittedDate.localeCompare(a.submittedDate);
        case 'date-asc':
          return a.submittedDate.localeCompare(b.submittedDate);
        case 'status':
          return a.status.localeCompare(b.status);
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    return filtered;
  }, [complaints, searchKeyword, startDate, endDate, sortBy]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredAndSortedComplaints.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentComplaints = filteredAndSortedComplaints.slice(startIndex, endIndex);

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  // Reset to page 1 when filters change
  const handleSearchChange = (value: string) => {
    setSearchKeyword(value);
    setCurrentPage(1);
  };

  const handleStartDateChange = (value: string) => {
    setStartDate(value);
    setCurrentPage(1);
  };

  const handleEndDateChange = (value: string) => {
    setEndDate(value);
    setCurrentPage(1);
  };

  const handleSortChange = (option: SortOption) => {
    setSortBy(option);
    setShowSortMenu(false);
    setCurrentPage(1);
  };

  const handleClearFilters = () => {
    setSearchKeyword('');
    setStartDate('');
    setEndDate('');
    setSortBy('date-desc');
    setCurrentPage(1);
  };

  const onGoHome = () => navigate('/applicant/main');

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          {/* 간단한 스피너 애니메이션 */}
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 font-medium">민원 내역을 불러오는 중입니다...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold text-gray-900">과거 민원 내역</h1>
            <Button
              onClick={onGoHome}
              variant="outline"
              className="h-11 px-6 text-base"
            >
              홈으로 돌아가기
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-6">
          {/* Filters Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="space-y-4">
              {/* Search and Sort Row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Search Input */}
                <div className="lg:col-span-2">
                  <Label htmlFor="search" className="text-base mb-2 block">
                    키워드 검색
                  </Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input
                      id="search"
                      type="text"
                      value={searchKeyword}
                      onChange={(e) => handleSearchChange(e.target.value)}
                      placeholder="민원 번호, 제목, 내용, 카테고리로 검색"
                      className="text-base h-12 pl-11"
                    />
                  </div>
                </div>

                {/* Sort Dropdown */}
                <div className="relative">
                  <Label className="text-base mb-2 block">정렬 기준</Label>
                  <Button
                    onClick={() => setShowSortMenu(!showSortMenu)}
                    variant="outline"
                    className="w-full h-12 justify-between text-base"
                  >
                    <span>{SORT_LABELS[sortBy]}</span>
                    <ArrowUpDown className="w-4 h-4 ml-2" />
                  </Button>
                  {showSortMenu && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                      {(Object.keys(SORT_LABELS) as SortOption[]).map((option) => (
                        <button
                          key={option}
                          onClick={() => handleSortChange(option)}
                          className={`w-full text-left px-4 py-3 text-base hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg ${sortBy === option ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-gray-700'
                            }`}
                        >
                          {SORT_LABELS[option]}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Date Range Row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="startDate" className="text-base mb-2 block">
                    시작 날짜
                  </Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input
                      id="startDate"
                      type="date"
                      value={startDate}
                      onChange={(e) => handleStartDateChange(e.target.value)}
                      className="text-base h-12 pl-11"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="endDate" className="text-base mb-2 block">
                    종료 날짜
                  </Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input
                      id="endDate"
                      type="date"
                      value={endDate}
                      onChange={(e) => handleEndDateChange(e.target.value)}
                      className="text-base h-12 pl-11"
                    />
                  </div>
                </div>

                <div className="flex items-end">
                  <Button
                    onClick={handleClearFilters}
                    variant="outline"
                    className="w-full h-12 text-base"
                  >
                    필터 초기화
                  </Button>
                </div>
              </div>
            </div>

            {/* Active Filters Summary */}
            {(searchKeyword || startDate || endDate || sortBy !== 'date-desc') && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm text-gray-600">활성 필터:</span>
                  {searchKeyword && (
                    <Badge variant="outline" className="text-sm">
                      검색: {searchKeyword}
                    </Badge>
                  )}
                  {startDate && (
                    <Badge variant="outline" className="text-sm">
                      시작: {startDate}
                    </Badge>
                  )}
                  {endDate && (
                    <Badge variant="outline" className="text-sm">
                      종료: {endDate}
                    </Badge>
                  )}
                  {sortBy !== 'date-desc' && (
                    <Badge variant="outline" className="text-sm">
                      정렬: {SORT_LABELS[sortBy]}
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Results Summary */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="bg-gray-100 px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <p className="text-gray-700 text-base">
                  총 <span className="font-bold text-lg">{filteredAndSortedComplaints.length}</span>건의 민원
                  {filteredAndSortedComplaints.length !== complaints.length && (
                    <span className="text-gray-500 text-sm ml-2">
                      (전체 {complaints.length}건 중)
                    </span>
                  )}
                </p>
                {totalPages > 0 && (
                  <p className="text-gray-600 text-sm">
                    {currentPage} / {totalPages} 페이지
                  </p>
                )}
              </div>
            </div>

            {/* Complaints List */}
            {currentComplaints.length > 0 ? (
              <div className="divide-y divide-gray-200">
                {currentComplaints.map((complaint) => (
                  <div
                    key={complaint.id}
                    className="p-6 hover:bg-gray-50 transition-colors"
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
                          <Badge className="bg-gray-100 text-gray-700 border border-gray-300 text-sm px-3 py-1">
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
                        onClick={() => handleViewDetail(complaint.id)}
                        className="bg-gray-900 hover:bg-gray-800 text-white h-11 px-6 flex items-center gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        상세보기
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              /* Empty State */
              <div className="p-12 text-center">
                <p className="text-gray-500 text-lg">검색 조건에 맞는 민원이 없습니다.</p>
                <p className="text-gray-400 text-sm mt-2">다른 검색어나 날짜 범위를 시도해보세요.</p>
              </div>
            )}

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
                    {Array.from({ length: Math.min(totalPages, 10) }, (_, i) => {
                      // Show first 3, last 3, and current page context
                      const pageNum = i + 1;
                      if (
                        pageNum <= 3 ||
                        pageNum > totalPages - 3 ||
                        (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
                      ) {
                        return (
                          <Button
                            key={pageNum}
                            onClick={() => goToPage(pageNum)}
                            variant={currentPage === pageNum ? 'default' : 'outline'}
                            className={`h-10 w-10 ${currentPage === pageNum
                              ? 'bg-gray-900 hover:bg-gray-800 text-white'
                              : 'hover:bg-gray-100'
                              }`}
                          >
                            {pageNum}
                          </Button>
                        );
                      } else if (pageNum === 4 || pageNum === totalPages - 3) {
                        return <span key={pageNum} className="px-2 text-gray-400">...</span>;
                      }
                      return null;
                    })}
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
        </div>
      </main>
    </div>
  );
}
