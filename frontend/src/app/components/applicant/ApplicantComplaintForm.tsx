import { useState } from 'react';
import { Home, FileText, MapPin } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { cn } from './ui/utils';
import KakaoMap from './KakaoMap';
import Swal from 'sweetalert2';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface NewComplaintFormProps {
  onGoHome: () => void;
  onViewComplaints: () => void;
  onPreview: (data: ComplaintFormData) => void;
}

export interface ComplaintFormData {
  title: string;
  body: string;
  location: string;
  incidentDate: Date;
}

export function ApplicantComplaintForm({ onGoHome, onViewComplaints, onPreview }: NewComplaintFormProps) {

  const navigate = useNavigate();
  const token = localStorage.getItem('accessToken');

  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [location, setLocation] = useState('서울특별시 강동구 성내로 25');
  const [incidentDate, setIncidentDate] = useState<Date>(new Date());
  // 위치 정보를 저장하기 위한 상태
  const [geoData, setGeoData] = useState({ lat: 0, lon: 0, roadAddress: '' });

  // 지도의 위치가 바뀔 때 실행될 함수
  const handleLocationChange = (lat: number, lon: number, roadAddress: string) => {
    // 1. 위도, 경도, 도로명 주소를 객체에 저장 (전송용)
    setGeoData({ lat, lon, roadAddress });

    // 2. 상단 Input 창에 표시되는 주소 텍스트를 마커 위치의 주소로 자동 업데이트!
    setLocation(roadAddress);
  };

  const handleSubmit = async () => {
    // 백엔드로 보낼 데이터 (DTO 구조)
    const submitData = {
      title,
      body,
      addressText: geoData.roadAddress || location,
      lat: geoData.lat,
      lon: geoData.lon,
    };

    Swal.fire({
      title: '민원을 제출하시겠습니까?',
      html: `<b>확인된 위치:</b><br/>${submitData.addressText}`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: '제출하기',
      cancelButtonText: '취소',
      confirmButtonColor: '#1677d3',
      cancelButtonColor: 'rgb(230, 190, 61)',
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          // 데이터 전송
          await axios.post('http://localhost:8080/api/applicant/complaint', submitData, {
            headers: {
              'Authorization': `Bearer ${token}`, // 반드시 Bearer 한 칸 띄우고 토큰 입력
              'Content-Type': 'application/json'
            }
          });

          // 전송 완료 알림
          Swal.fire({
            title: '전송 완료!',
            text: '민원이 정상적으로 접수되었습니다.',
            icon: 'success',
            confirmButtonText: '확인'
          }).then(() => {
            navigate('/applicant/main');
          });

        } catch (error) {
          Swal.fire('오류 발생', '민원 전송 중 에러가 발생했습니다.', 'error');
        }
      }
    });
  };

  const handlePreview = () => {
    const formData: ComplaintFormData = {
      title,
      body,
      location,
      incidentDate,
    };
    onPreview(formData);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">새 민원 작성</h1>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={onGoHome}
              className="flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              홈으로
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate('/applicant/complaints')}
              className="flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              과거 민원 보기
            </Button>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
          {/* Title Input */}
          <div className="space-y-2">
            <div className="flex justify-between items-end">
              <Label htmlFor="title" className="font-semibold text-gray-700">민원 제목 *</Label>
              <span className={cn(
                "text-xs",
                title.length >= 200 ? "text-red-500 font-bold" : "text-gray-400"
              )}>
                {title.length} / 200
              </span>
            </div>
            <Input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value.slice(0, 200))}
              placeholder="예: 아파트 주변 가로등 고장"
              className="w-full border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all shadow-sm"
            />
          </div>
          {/* Body Textarea */}
          <div className="space-y-2">
            <div className="flex justify-between items-end">
              <Label htmlFor="body" className="font-semibold text-gray-700">민원 내용 *</Label>
              <span className={cn(
                "text-xs",
                body.length >= 40000 ? "text-red-500 font-bold" : "text-gray-400"
              )}>
                {body.length.toLocaleString()} / 40,000
              </span>
            </div>
            <Textarea
              id="body"
              value={body}
              onChange={(e) => setBody(e.target.value.slice(0, 40000))}
              placeholder="민원 내용을 상세히 작성해주세요."
              className="w-full min-h-[300px] resize-y border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all p-4 shadow-sm"
            />
          </div>

          {/* Location with Map API Space */}
          <div className="space-y-2">
            <Label htmlFor="location">발생 장소 *</Label>
            <div className="space-y-3">
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  id="location"
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full pl-10"
                  placeholder="주소를 입력하세요"
                />
              </div>

              {/* Map API Integration Space */}
              <div className="w-full h-64 bg-gray-100 rounded-lg border border-gray-300 overflow-hidden relative">
                {/* 주소가 있을 때만 지도를 보여주거나, 기본 지도를 보여줍니다 */}
                <KakaoMap address={location}
                  onLocationChange={handleLocationChange} />
              </div>
            </div>
          </div>

          {/* Incident Date with Calendar */}
          <div className="space-y-2">
            <Label htmlFor="incidentDate">발생 일자 *</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !incidentDate && "text-muted-foreground"
                  )}
                >
                  {incidentDate ? (
                    format(incidentDate, "PPP", { locale: ko })
                  ) : (
                    <span>날짜를 선택하세요</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={incidentDate}
                  onSelect={(date) => date && setIncidentDate(date)}
                  initialFocus
                  locale={ko}
                />
              </PopoverContent>
            </Popover>
            <p className="text-xs text-gray-500">
              사건이 발생한 날짜를 선택해주세요 (기본값: 오늘)
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              onClick={handlePreview}
              variant="outline"
              className="flex-1"
              disabled={!title || !body || !location}
            >
              미리보기
            </Button>
            <Button
              onClick={handleSubmit}
              className="flex-1"
              disabled={!title || !body || !location}
            >
              제출하기
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}

