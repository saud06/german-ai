'use client';

import { useLearningPath, usePathLocations } from '@/hooks/useLearningPath';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeftIcon, CheckCircleIcon, LockIcon, PlayCircleIcon } from 'lucide-react';

export default function LearningPathMapPage() {
  const params = useParams();
  const router = useRouter();
  const pathId = params.id as string;
  
  const { data: pathData, isLoading: pathLoading } = useLearningPath(pathId);
  const { data: locations, isLoading: locationsLoading } = usePathLocations(pathId);

  if (pathLoading || locationsLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading your journey map...</p>
        </div>
      </div>
    );
  }

  if (!pathData || !locations) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400">Chapter not found</p>
          <Link href="/learning-path" className="text-indigo-400 hover:text-indigo-300 mt-2 inline-block">
            ← Back to Learning Path
          </Link>
        </div>
      </div>
    );
  }

  const { path, progress } = pathData;

  return (
    <div className="min-h-screen bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-6">
          <Link 
            href="/learning-path"
            className="inline-flex items-center gap-2 text-indigo-400 hover:text-indigo-300 mb-4 transition-colors"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Back to Journey
          </Link>
          
          <div className="bg-gray-800 rounded-xl shadow-2xl p-6 border border-gray-700">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-full text-sm font-semibold border border-indigo-500/30">
                    {path.level}
                  </span>
                  <span className="text-gray-400">Chapter {path.chapter}</span>
                </div>
                <h1 className="text-3xl font-bold text-white mb-2">{path.title}</h1>
                <p className="text-gray-400">{path.description}</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-indigo-400">
                  {progress?.progress_percent || 0}%
                </div>
                <div className="text-sm text-gray-500">Complete</div>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-4">
              <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${progress?.progress_percent || 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Map - Winding Path Design */}
        <div className="bg-gray-800 rounded-xl shadow-2xl p-8 mb-6 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-6 text-center flex items-center justify-center gap-2">
            <span className="text-3xl">🗺️</span>
            <span>Your Learning Journey</span>
          </h2>
          
          {/* Winding Path Map */}
          <style jsx>{`
            .hover-marker:hover circle {
              filter: brightness(1.1) drop-shadow(0 6px 8px rgba(0,0,0,0.4));
              transform-origin: center;
            }
          `}</style>
          <div className="relative bg-gradient-to-br from-gray-900 via-indigo-950 to-purple-950 rounded-2xl p-8 overflow-hidden shadow-inner" style={{ minHeight: '800px' }}>
            {/* Enhanced World Map Background */}
            <div className="absolute inset-0 opacity-8">
              <svg viewBox="0 0 1200 700" className="w-full h-full">
                {/* Continents - more detailed */}
                <g fill="#6366f1" opacity="0.06">
                  {/* North America */}
                  <path d="M100,150 Q120,140 140,145 L160,140 Q180,135 200,145 L220,150 Q240,160 250,180 L240,200 Q230,220 210,230 L190,240 Q170,245 150,240 L130,230 Q110,220 100,200 Z" />
                  {/* Europe */}
                  <path d="M400,120 Q420,115 440,120 L460,125 Q480,130 490,145 L485,165 Q480,180 465,185 L445,188 Q425,185 410,175 L400,160 Q395,140 400,120 Z" />
                  {/* Asia */}
                  <path d="M600,100 Q650,95 700,105 L750,115 Q800,125 830,145 L840,170 Q845,195 835,220 L810,245 Q780,260 740,265 L690,260 Q640,250 610,230 L590,200 Q585,170 590,140 L595,120 Q598,110 600,100 Z" />
                  {/* Africa */}
                  <path d="M350,280 Q380,275 410,285 L430,300 Q445,320 450,345 L445,380 Q435,410 415,430 L390,445 Q365,450 340,440 L320,420 Q305,395 305,365 L310,330 Q320,300 335,285 Z" />
                  {/* South America */}
                  <path d="M200,350 Q220,345 240,355 L255,375 Q265,400 260,425 L250,455 Q235,480 215,490 L195,485 Q175,475 165,455 L160,425 Q160,395 170,370 L185,355 Z" />
                  {/* Australia */}
                  <path d="M750,420 Q780,415 810,425 L830,440 Q845,460 840,485 L825,505 Q805,515 780,510 L760,500 Q745,485 745,465 L748,445 Q750,430 750,420 Z" />
                </g>
              </svg>
            </div>
            
            <svg viewBox="0 0 1200 700" className="w-full h-auto relative z-10" preserveAspectRatio="xMidYMid meet">
              <defs>
                {/* Road gradient */}
                <linearGradient id="roadGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#4b5563', stopOpacity: 1 }} />
                  <stop offset="50%" style={{ stopColor: '#374151', stopOpacity: 1 }} />
                  <stop offset="100%" style={{ stopColor: '#4b5563', stopOpacity: 1 }} />
                </linearGradient>
                
                {/* Completed gradient */}
                <linearGradient id="completedGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#10b981', stopOpacity: 1 }} />
                  <stop offset="100%" style={{ stopColor: '#059669', stopOpacity: 1 }} />
                </linearGradient>
                
                {/* Active gradient */}
                <linearGradient id="activeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#6366f1', stopOpacity: 1 }} />
                  <stop offset="100%" style={{ stopColor: '#8b5cf6', stopOpacity: 1 }} />
                </linearGradient>
                
                {/* Locked gradient */}
                <linearGradient id="lockedGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#d1d5db', stopOpacity: 1 }} />
                  <stop offset="100%" style={{ stopColor: '#9ca3af', stopOpacity: 1 }} />
                </linearGradient>
                
                {/* Glow effect */}
                <filter id="glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                
                {/* Shadow */}
                <filter id="shadow">
                  <feDropShadow dx="0" dy="4" stdDeviation="4" floodOpacity="0.3"/>
                </filter>
              </defs>
              
              {/* City Elements - Buildings, Trees, Lamp Posts */}
              <g opacity="0.3">
                {/* Buildings along the path */}
                <g fill="#94a3b8">
                  {/* Left side buildings */}
                  <rect x="80" y="480" width="40" height="60" rx="2" />
                  <rect x="130" y="500" width="35" height="40" rx="2" />
                  <rect x="200" y="520" width="45" height="30" rx="2" />
                  
                  {/* Right side buildings */}
                  <rect x="900" y="120" width="50" height="70" rx="2" />
                  <rect x="960" y="140" width="40" height="50" rx="2" />
                  <rect x="1020" y="100" width="45" height="80" rx="2" />
                  
                  {/* Middle buildings */}
                  <rect x="500" y="380" width="35" height="45" rx="2" />
                  <rect x="550" y="400" width="40" height="35" rx="2" />
                </g>
                
                {/* Windows on buildings */}
                <g fill="#cbd5e1">
                  <rect x="90" y="490" width="8" height="8" rx="1" />
                  <rect x="105" y="490" width="8" height="8" rx="1" />
                  <rect x="90" y="505" width="8" height="8" rx="1" />
                  <rect x="105" y="505" width="8" height="8" rx="1" />
                  
                  <rect x="910" y="135" width="10" height="10" rx="1" />
                  <rect x="925" y="135" width="10" height="10" rx="1" />
                  <rect x="910" y="150" width="10" height="10" rx="1" />
                  <rect x="925" y="150" width="10" height="10" rx="1" />
                </g>
                
                {/* Trees */}
                <g>
                  {/* Left trees */}
                  <ellipse cx="170" cy="570" rx="20" ry="25" fill="#86efac" />
                  <rect x="167" y="570" width="6" height="20" fill="#78716c" />
                  
                  <ellipse cx="280" cy="540" rx="18" ry="22" fill="#86efac" />
                  <rect x="277" y="540" width="6" height="18" fill="#78716c" />
                  
                  {/* Right trees */}
                  <ellipse cx="850" cy="180" rx="22" ry="28" fill="#86efac" />
                  <rect x="847" y="180" width="6" height="22" fill="#78716c" />
                  
                  <ellipse cx="1050" cy="90" rx="20" ry="25" fill="#86efac" />
                  <rect x="1047" y="90" width="6" height="20" fill="#78716c" />
                </g>
                
                {/* Lamp Posts */}
                <g stroke="#94a3b8" strokeWidth="3" fill="none">
                  {/* Left side lamps */}
                  <line x1="150" y1="560" x2="150" y2="520" />
                  <circle cx="150" cy="515" r="5" fill="#fbbf24" opacity="0.6" />
                  
                  <line x1="320" y1="510" x2="320" y2="470" />
                  <circle cx="320" cy="465" r="5" fill="#fbbf24" opacity="0.6" />
                  
                  {/* Right side lamps */}
                  <line x1="800" y1="250" x2="800" y2="210" />
                  <circle cx="800" cy="205" r="5" fill="#fbbf24" opacity="0.6" />
                  
                  <line x1="980" y1="180" x2="980" y2="140" />
                  <circle cx="980" cy="135" r="5" fill="#fbbf24" opacity="0.6" />
                </g>
                
                {/* Clouds */}
                <g fill="#e0e7ff" opacity="0.5">
                  <ellipse cx="200" cy="80" rx="40" ry="20" />
                  <ellipse cx="230" cy="75" rx="35" ry="18" />
                  
                  <ellipse cx="700" cy="50" rx="45" ry="22" />
                  <ellipse cx="735" cy="48" rx="38" ry="20" />
                  
                  <ellipse cx="1000" cy="70" rx="42" ry="21" />
                </g>
              </g>
              
              {/* Winding Road Path */}
              {locations && locations.length > 0 && (() => {
                // Create serpentine path: bottom-left to top-right with smooth waves
                const pathCoords = locations.map((_, idx) => {
                  const totalWidth = 1100;
                  const spacing = totalWidth / (locations.length > 1 ? locations.length - 1 : 1);
                  const x = 50 + (idx * spacing);
                  
                  // Diagonal progression: start low (bottom-left), end high (top-right)
                  const progress = idx / (locations.length - 1);
                  const diagonalY = 550 - (progress * 350); // 550 (bottom) to 200 (top)
                  
                  // Add smooth serpentine waves
                  // Dynamic frequency based on number of locations
                  const wavesPerPath = Math.max(2, Math.floor(locations.length / 2)); // 2-3 waves
                  const frequency = (wavesPerPath * Math.PI) / (locations.length - 1);
                  const amplitude = 80; // Moderate wave height
                  
                  // Combine diagonal with sine wave
                  const waveOffset = Math.sin(idx * frequency) * amplitude;
                  const y = diagonalY + waveOffset;
                  
                  return { x, y };
                });
                
                // Build SVG path string for smooth curves
                let pathString = `M ${pathCoords[0].x} ${pathCoords[0].y}`;
                for (let i = 1; i < pathCoords.length; i++) {
                  const curr = pathCoords[i];
                  const prev = pathCoords[i - 1];
                  const controlY = (prev.y + curr.y) / 2;
                  const controlX1 = prev.x + 80;
                  const controlX2 = curr.x - 80;
                  pathString += ` C ${controlX1} ${controlY}, ${controlX2} ${controlY}, ${curr.x} ${curr.y}`;
                }
                
                return (
                  <g>
                    {/* Road shadow */}
                    <path
                      d={pathString}
                      fill="none"
                      stroke="rgba(0,0,0,0.15)"
                      strokeWidth="100"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      transform="translate(5, 5)"
                    />
                    
                    {/* Main road */}
                    <path
                      d={pathString}
                      fill="none"
                      stroke="url(#roadGradient)"
                      strokeWidth="95"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    
                    {/* Road center line (dashed) */}
                    <path
                      d={pathString}
                      fill="none"
                      stroke="white"
                      strokeWidth="5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeDasharray="25,20"
                      opacity="0.6"
                    />
                  </g>
                );
              })()}
              
              {/* Location markers */}
              {locations && locations.length > 0 && locations.map((locData, idx) => {
                const { location, is_unlocked, is_completed } = locData;
                
                // Calculate position matching diagonal serpentine path
                const totalWidth = 1100;
                const spacing = totalWidth / (locations.length > 1 ? locations.length - 1 : 1);
                const x = 50 + (idx * spacing);
                
                // Same diagonal + wave pattern as path
                const progress = idx / (locations.length - 1);
                const diagonalY = 550 - (progress * 350);
                
                const wavesPerPath = Math.max(2, Math.floor(locations.length / 2));
                const frequency = (wavesPerPath * Math.PI) / (locations.length - 1);
                const amplitude = 80;
                
                const waveOffset = Math.sin(idx * frequency) * amplitude;
                const y = diagonalY + waveOffset;
                
                const isAbove = waveOffset < 0; // Above when wave offset is negative
                
                return (
                  <g 
                    key={location._id}
                    className={`transition-all duration-300 ${is_unlocked ? "cursor-pointer" : "cursor-not-allowed"}`}
                    onClick={() => is_unlocked && router.push(`/learning-path/locations/${location._id}`)}
                  >
                    {/* Pulse animation for active locations */}
                    {is_unlocked && !is_completed && (
                      <circle
                        cx={x}
                        cy={y}
                        r="40"
                        fill={is_unlocked ? "#6366f1" : "#d1d5db"}
                        opacity="0.2"
                      >
                        <animate
                          attributeName="r"
                          from="40"
                          to="60"
                          dur="2s"
                          repeatCount="indefinite"
                        />
                        <animate
                          attributeName="opacity"
                          from="0.2"
                          to="0"
                          dur="2s"
                          repeatCount="indefinite"
                        />
                      </circle>
                    )}
                    
                    {/* Circular marker with gradient - fixed hover */}
                    <g className={is_unlocked ? "hover-marker" : ""}>
                      <circle
                        cx={x}
                        cy={y}
                        r="40"
                        fill={is_completed ? "url(#completedGradient)" : is_unlocked ? "url(#activeGradient)" : "url(#lockedGradient)"}
                        stroke="white"
                        strokeWidth="5"
                        filter="url(#shadow)"
                      />
                    </g>
                    
                    {/* Icon */}
                    <text
                      x={x}
                      y={y + 8}
                      textAnchor="middle"
                      fontSize="28"
                      fontWeight="bold"
                      fill="white"
                      className="pointer-events-none"
                    >
                      {is_completed ? "✓" : is_unlocked ? "★" : "🔒"}
                    </text>
                    
                    {/* Location number badge - on top with higher z-index */}
                    <g style={{ zIndex: 100 }}>
                      <circle
                        cx={x}
                        cy={y - 55}
                        r="18"
                        fill="white"
                        stroke={is_completed ? "#10b981" : is_unlocked ? "#6366f1" : "#9ca3af"}
                        strokeWidth="3"
                        filter="url(#shadow)"
                      />
                      <text
                        x={x}
                        y={y - 47}
                        textAnchor="middle"
                        fontSize="16"
                        fontWeight="bold"
                        fill={is_completed ? "#10b981" : is_unlocked ? "#6366f1" : "#9ca3af"}
                        className="pointer-events-none"
                      >
                        {idx + 1}
                      </text>
                    </g>
                    
                    {/* Info card - positioned above or below */}
                    <g transform={`translate(${x}, ${isAbove ? y - 80 : y + 80})`}>
                      <rect
                        x="-90"
                        y={isAbove ? "-60" : "0"}
                        width="180"
                        height="60"
                        rx="10"
                        fill="#1f2937"
                        stroke={is_completed ? "#10b981" : is_unlocked ? "#6366f1" : "#4b5563"}
                        strokeWidth="2.5"
                        filter="url(#shadow)"
                      />
                      <text
                        x="0"
                        y={isAbove ? "-35" : "25"}
                        textAnchor="middle"
                        fontSize="15"
                        fontWeight="bold"
                        fill="#ffffff"
                      >
                        {location.name}
                      </text>
                      <text
                        x="0"
                        y={isAbove ? "-15" : "45"}
                        textAnchor="middle"
                        fontSize="12"
                        fill="#9ca3af"
                      >
                        ⏱️ {location.estimated_minutes} min
                      </text>
                    </g>
                    
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Legend */}
          <div className="mt-8 flex items-center justify-center gap-8 text-sm">
            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 rounded-lg border border-green-500/30">
              <div className="w-4 h-4 rounded-full bg-gradient-to-br from-green-500 to-green-600"></div>
              <span className="text-green-400 font-medium">Completed</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-indigo-500/20 rounded-lg border border-indigo-500/30">
              <div className="w-4 h-4 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600"></div>
              <span className="text-indigo-400 font-medium">Available</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-700 rounded-lg border border-gray-600">
              <div className="w-4 h-4 rounded-full bg-gradient-to-br from-gray-400 to-gray-500"></div>
              <span className="text-gray-400 font-medium">Locked</span>
            </div>
          </div>
        </div>

        {/* Location List */}
        <div className="bg-gray-800 rounded-xl shadow-2xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Locations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {locations.map((locData) => {
              const { location, is_unlocked, is_completed, completion_percent } = locData;
              
              return (
                <Link
                  key={location._id}
                  href={is_unlocked ? `/learning-path/locations/${location._id}` : '#'}
                  className={`border-2 rounded-lg p-4 transition-all ${
                    is_unlocked 
                      ? 'border-indigo-500/30 bg-gray-700/50 hover:border-indigo-400 hover:bg-gray-700 hover:shadow-lg cursor-pointer' 
                      : 'border-gray-700 bg-gray-800/50 opacity-50 cursor-not-allowed'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-bold text-white">{location.name}</h3>
                    <div>
                      {is_completed && <CheckCircleIcon className="w-6 h-6 text-green-500" />}
                      {!is_completed && is_unlocked && <PlayCircleIcon className="w-6 h-6 text-indigo-500" />}
                      {!is_unlocked && <LockIcon className="w-6 h-6 text-gray-400" />}
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-400 mb-3">{location.description}</p>
                  
                  {is_unlocked && (
                    <>
                      <div className="w-full bg-gray-600 rounded-full h-2 mb-2">
                        <div 
                          className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all"
                          style={{ width: `${completion_percent}%` }}
                        ></div>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-400">
                        <span>⏱️ {location.estimated_minutes} min</span>
                        <span>{location.scenarios.length} scenarios</span>
                      </div>
                    </>
                  )}
                  
                  {!is_unlocked && (
                    <div className="text-xs text-gray-400">
                      🔒 Complete previous locations to unlock
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
          
          {/* No locations message */}
          {(!locations || locations.length === 0) && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🗺️</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Chapter Map Coming Soon
              </h3>
              <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                This chapter doesn't have any locations yet. Check back later as we add more content to your learning journey!
              </p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
