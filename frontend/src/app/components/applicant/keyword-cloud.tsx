import { useEffect, useRef } from 'react';
// import ReactWordcloud from 'react-wordcloud';

interface KeywordCloudProps {
  keywords: {
    text: string;
    value: number;
  }[];
}

export function KeywordCloud({ keywords }: KeywordCloudProps) {
  const options = {
    rotations: 2,
    rotationAngles: [-90, 0],
    fontSizes: [16, 60] as [number, number],
    padding: 2,
    spiral: 'archimedean' as const,
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold mb-4 text-gray-900">민원 키워드 분석</h2>
      <div className="h-64">
        <ReactWordcloud words={keywords} options={options} />
      </div>
      <p className="text-xs text-gray-500 text-center mt-4">
        * 최근 한 달간 가장 많이 언급된 키워드
      </p>
    </div>
  );
}