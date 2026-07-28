import { SkeletonSpotlight, SkeletonNewsList, SkeletonCard } from "../components/Skeletons";

export default function Loading() {
  return (
    <div className="space-y-12">
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <SkeletonSpotlight />
        <SkeletonNewsList />
      </div>
      
      <div className="space-y-6">
        <div className="h-6 w-48 bg-white/5 rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    </div>
  );
}
