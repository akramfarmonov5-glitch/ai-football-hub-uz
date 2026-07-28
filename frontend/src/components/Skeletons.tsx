export function SkeletonCard() {
  return (
    <div className="glass-panel rounded-2xl p-5 border border-white/5 animate-pulse">
      {/* Top badges */}
      <div className="flex items-center justify-between mb-4">
        <div className="h-4 w-24 bg-white/5 rounded-full" />
        <div className="h-4 w-12 bg-white/5 rounded-full" />
      </div>

      {/* Teams */}
      <div className="flex items-center justify-between py-4">
        <div className="flex flex-col items-center space-y-2 flex-1">
          <div className="w-12 h-12 bg-white/5 rounded-xl" />
          <div className="h-3 w-16 bg-white/5 rounded" />
        </div>
        <div className="h-6 w-12 bg-white/5 rounded mx-4" />
        <div className="flex flex-col items-center space-y-2 flex-1">
          <div className="w-12 h-12 bg-white/5 rounded-xl" />
          <div className="h-3 w-16 bg-white/5 rounded" />
        </div>
      </div>

      {/* Probability bar */}
      <div className="mt-4 pt-3 border-t border-white/5 space-y-2">
        <div className="flex justify-between">
          <div className="h-2 w-20 bg-white/5 rounded" />
          <div className="h-2 w-28 bg-white/5 rounded" />
        </div>
        <div className="h-1 w-full bg-white/5 rounded-full" />
      </div>
    </div>
  );
}

export function SkeletonSpotlight() {
  return (
    <div className="xl:col-span-2 rounded-3xl border border-white/10 bg-gradient-to-br from-slate-950 via-[#0a0f1d] to-[#04060d] p-8 min-h-[400px] animate-pulse">
      <div className="flex items-center justify-between mb-8">
        <div className="h-5 w-48 bg-white/5 rounded-full" />
        <div className="h-5 w-16 bg-white/5 rounded-full" />
      </div>

      <div className="grid grid-cols-3 items-center py-12 text-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-20 h-20 bg-white/5 rounded-2xl" />
          <div className="h-4 w-24 bg-white/5 rounded" />
        </div>
        <div className="flex flex-col items-center">
          <div className="h-16 w-28 bg-white/5 rounded-xl" />
        </div>
        <div className="flex flex-col items-center space-y-4">
          <div className="w-20 h-20 bg-white/5 rounded-2xl" />
          <div className="h-4 w-24 bg-white/5 rounded" />
        </div>
      </div>

      <div className="pt-6 border-t border-white/5 space-y-3">
        <div className="h-3 w-20 bg-white/5 rounded" />
        <div className="h-3 w-3/4 bg-white/5 rounded" />
        <div className="h-1.5 w-full bg-white/5 rounded-full mt-2" />
      </div>
    </div>
  );
}

export function SkeletonNewsList() {
  return (
    <div className="flex flex-col space-y-6">
      <div className="flex items-center border-b border-white/5 pb-4">
        <div className="h-5 w-36 bg-white/5 rounded animate-pulse" />
      </div>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass-panel rounded-2xl overflow-hidden animate-pulse">
            <div className="w-full h-28 bg-white/5" />
            <div className="p-4 space-y-3">
              <div className="h-4 w-3/4 bg-white/5 rounded" />
              <div className="h-3 w-full bg-white/5 rounded" />
              <div className="h-3 w-1/2 bg-white/5 rounded" />
              <div className="flex justify-between">
                <div className="h-2 w-16 bg-white/5 rounded" />
                <div className="h-2 w-12 bg-white/5 rounded" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
