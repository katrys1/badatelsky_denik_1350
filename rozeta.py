import React from 'react';

const StainedGlassReward = ({ xp, maxXp }) => {
  const percentage = Math.min((xp / maxXp) * 100, 100);
  const totalSegments = 8;
  const completedSegments = Math.floor((percentage / 100) * totalSegments);
  const isMaxed = percentage === 100;

  // Barvy pro vitráž (střídání odstínů)
  const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#6366f1', '#a855f7'];

  // Funkce pro výpočet SVG cesty kruhové výseče
  const getSegmentPath = (index) => {
    const angle = (360 / totalSegments);
    const startAngle = index * angle;
    const endAngle = (index + 1) * angle;
    
    const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
      const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
      return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
      };
    };

    const start = polarToCartesian(100, 100, 80, endAngle);
    const end = polarToCartesian(100, 100, 80, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

    return [
      "M", 100, 100, 
      "L", start.x, start.y, 
      "A", 80, 80, 0, largeArcFlag, 0, end.x, end.y,
      "Z"
    ].join(" ");
  };

  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-slate-950 z-50 transition-all duration-1000">
      <div className={`relative transition-all duration-1000 ${isMaxed ? 'scale-110' : 'scale-100'}`}>
        
        {/* SVG Rozeta */}
        <svg width="400" height="400" viewBox="0 0 200 200" className="drop-shadow-2xl">
          <defs>
            {/* Efekt záření pro 100% XP */}
            <filter id="glow">
              <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          <g filter={isMaxed ? "url(#glow)" : ""}>
            {/* Vykreslení segmentů */}
            {[...Array(totalSegments)].map((_, i) => (
              <path
                key={i}
                d={getSegmentPath(i)}
                fill={i < completedSegments ? colors[i] : '#1e293b'}
                stroke="#0f172a"
                strokeWidth="2"
                className="transition-all duration-700 ease-in-out"
                style={{
                  opacity: i < completedSegments ? 0.9 : 0.3,
                }}
              />
            ))}
            
            {/* Centrální kámen */}
            <circle 
              cx="100" cy="100" r="15" 
              fill={isMaxed ? "#fff" : "#334155"} 
              className="transition-colors duration-1000"
            />
          </g>
        </svg>

        {/* Textové info */}
        <div className="mt-8 text-center">
          <h2 className={`text-3xl font-serif font-bold uppercase tracking-widest ${isMaxed ? 'text-yellow-400 animate-pulse' : 'text-slate-400'}`}>
            {isMaxed ? 'Dosaženo Osvícení' : `Pokrok: ${Math.round(percentage)}%`}
          </h2>
          <p className="text-slate-500 mt-2 font-mono">{xp} / {maxXp} XP</p>
        </div>
      </div>
    </div>
  );
};

export default StainedGlassReward;