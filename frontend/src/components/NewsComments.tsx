"use client";

import { useState, useEffect } from "react";
import { MessageSquare, Send, ThumbsUp, Heart, Flame, Trophy } from "lucide-react";

interface Comment {
  id: string;
  author: string;
  text: string;
  time: string;
}

export function NewsComments({ newsSlug }: { newsSlug: string }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [author, setAuthor] = useState("");
  const [text, setText] = useState("");
  const [reactions, setReactions] = useState<{ [key: string]: number }>({
    soccer: 12,
    flame: 8,
    heart: 15,
    like: 9,
  });
  const [userReacted, setUserReacted] = useState<{ [key: string]: boolean }>({});

  useEffect(() => {
    const key = `comments_${newsSlug}`;
    const saved = localStorage.getItem(key);
    if (saved) {
      try {
        setComments(JSON.parse(saved));
      } catch (err) {
        console.error(err);
      }
    }
  }, [newsSlug]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    const newComment: Comment = {
      id: Date.now().toString(),
      author: author.trim() || "Muxlis",
      text: text.trim(),
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const updated = [newComment, ...comments];
    setComments(updated);
    localStorage.setItem(`comments_${newsSlug}`, JSON.stringify(updated));
    setText("");
  };

  const toggleReaction = (type: string) => {
    const isSet = userReacted[type];
    setUserReacted((prev) => ({ ...prev, [type]: !isSet }));
    setReactions((prev) => ({
      ...prev,
      [type]: prev[type] + (isSet ? -1 : 1),
    }));
  };

  return (
    <div className="glass-panel p-6 md:p-8 rounded-3xl space-y-8 mt-10 border border-white/10">
      {/* Reactions Section */}
      <div className="space-y-3 border-b border-white/10 pb-6">
        <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
          Reaksiyangizni bildiring:
        </h3>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => toggleReaction("soccer")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
              userReacted.soccer
                ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-300"
                : "bg-white/5 border-white/10 text-slate-300 hover:bg-white/10"
            }`}
          >
            <Trophy className="w-4 h-4 text-emerald-400" />
            <span>Zo'r! ({reactions.soccer})</span>
          </button>

          <button
            onClick={() => toggleReaction("flame")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
              userReacted.flame
                ? "bg-amber-500/20 border-amber-500/50 text-amber-300"
                : "bg-white/5 border-white/10 text-slate-300 hover:bg-white/10"
            }`}
          >
            <Flame className="w-4 h-4 text-amber-400" />
            <span>Qaynoq ({reactions.flame})</span>
          </button>

          <button
            onClick={() => toggleReaction("heart")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
              userReacted.heart
                ? "bg-rose-500/20 border-rose-500/50 text-rose-300"
                : "bg-white/5 border-white/10 text-slate-300 hover:bg-white/10"
            }`}
          >
            <Heart className="w-4 h-4 text-rose-400" />
            <span>Yoqdi ({reactions.heart})</span>
          </button>

          <button
            onClick={() => toggleReaction("like")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
              userReacted.like
                ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300"
                : "bg-white/5 border-white/10 text-slate-300 hover:bg-white/10"
            }`}
          >
            <ThumbsUp className="w-4 h-4 text-cyan-400" />
            <span>Tasanno ({reactions.like})</span>
          </button>
        </div>
      </div>

      {/* Comment Form */}
      <div className="space-y-4">
        <h3 className="text-base font-extrabold text-slate-100 flex items-center">
          <MessageSquare className="w-4 h-4 mr-2 text-emerald-400" />
          Izoh qoldirish ({comments.length})
        </h3>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="text"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            placeholder="Ismingiz yoki taxallusingiz (Ixtiyoriy)"
            className="w-full bg-slate-950/50 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50"
          />

          <div className="relative">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Ushbu yangilik haqida fikringizni yozing..."
              rows={3}
              className="w-full bg-slate-950/50 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 resize-none"
              required
            />
            <button
              type="submit"
              className="absolute bottom-3 right-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 px-4 py-1.5 rounded-lg text-xs font-bold hover:opacity-90 transition-opacity flex items-center space-x-1.5 cursor-pointer shadow-md shadow-emerald-500/20"
            >
              <span>Yuborish</span>
              <Send className="w-3 h-3" />
            </button>
          </div>
        </form>
      </div>

      {/* Comments List */}
      <div className="space-y-4">
        {comments.length === 0 ? (
          <p className="text-xs text-slate-500 text-center py-4">
            Birinchi bo'lib izoh qoldiring! 💬
          </p>
        ) : (
          comments.map((c) => (
            <div
              key={c.id}
              className="bg-white/5 border border-white/5 p-4 rounded-2xl space-y-1.5 animate-fadeIn"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400">{c.author}</span>
                <span className="text-[10px] text-slate-500">{c.time}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{c.text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
