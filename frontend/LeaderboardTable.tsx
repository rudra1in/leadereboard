// React component for interactive leaderboard table
// This component is hydrated client-side for interactivity

import React, { useState, useEffect } from 'react';

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  display_name?: string;
  avatar_url?: string;
  total_score: number;
  score_count: number;
  percentile: number;
  last_score_at?: string;
}

interface LeaderboardTableProps {
  entries: LeaderboardEntry[];
  page: number;
  pageSize: number;
  totalPages: number;
  totalUsers: number;
}

export default function LeaderboardTable({
  entries,
  page,
  pageSize,
  totalPages,
  totalUsers,
}: LeaderboardTableProps) {
  const [sortBy, setSortBy] = useState<'score' | 'rank' | 'games'>('rank');
  const [sortedEntries, setSortedEntries] = useState(entries);

  useEffect(() => {
    const sorted = [...entries].sort((a, b) => {
      if (sortBy === 'score') {
        return b.total_score - a.total_score;
      } else if (sortBy === 'games') {
        return b.score_count - a.score_count;
      }
      return a.rank - b.rank;
    });
    setSortedEntries(sorted);
  }, [sortBy, entries]);

  const getRankMedal = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return String(rank).padStart(2, '0');
    }
  };

  const formatScore = (score: number) => {
    return score.toLocaleString('en-US');
  };

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-controls">
        <div className="sort-buttons">
          <button
            className={`sort-btn ${sortBy === 'rank' ? 'active' : ''}`}
            onClick={() => setSortBy('rank')}
          >
            Rank
          </button>
          <button
            className={`sort-btn ${sortBy === 'score' ? 'active' : ''}`}
            onClick={() => setSortBy('score')}
          >
            Score
          </button>
          <button
            className={`sort-btn ${sortBy === 'games' ? 'active' : ''}`}
            onClick={() => setSortBy('games')}
          >
            Games
          </button>
        </div>
        <div className="stats">
          <span>Total Players: {totalUsers}</span>
          <span>Page: {page}/{totalPages}</span>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th className="rank-col">Rank</th>
              <th className="player-col">Player</th>
              <th className="score-col">Score</th>
              <th className="games-col">Games</th>
              <th className="percentile-col">Percentile</th>
            </tr>
          </thead>
          <tbody>
            {sortedEntries.map((entry) => (
              <tr key={entry.user_id} className={`rank-row rank-${entry.rank}`}>
                <td className="rank-cell">
                  <span className={`rank-badge rank-${entry.rank}`}>
                    {getRankMedal(entry.rank)}
                  </span>
                </td>
                <td className="player-cell">
                  <a href={`/profile/${entry.username}`} className="player-link">
                    {entry.display_name || entry.username}
                  </a>
                </td>
                <td className="score-cell">
                  <span className="score-value">{formatScore(entry.total_score)}</span>
                </td>
                <td className="games-cell">{entry.score_count}</td>
                <td className="percentile-cell">{entry.percentile.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style jsx>{`
        .leaderboard-container {
          background-color: white;
          border-radius: 0.75rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }

        .leaderboard-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #f9fafb;
          border-bottom: 1px solid #e5e7eb;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .sort-buttons {
          display: flex;
          gap: 0.5rem;
        }

        .sort-btn {
          padding: 0.5rem 1rem;
          background-color: white;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          cursor: pointer;
          font-weight: 500;
          color: #4b5563;
          transition: all 0.2s;

          &:hover {
            border-color: #3b82f6;
            color: #3b82f6;
          }

          &.active {
            background-color: #3b82f6;
            color: white;
            border-color: #3b82f6;
          }
        }

        .stats {
          display: flex;
          gap: 1.5rem;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .table-wrapper {
          overflow-x: auto;
        }

        .leaderboard-table {
          width: 100%;
          border-collapse: collapse;
          background-color: white;
        }

        thead {
          background-color: #f3f4f6;
          border-bottom: 2px solid #d1d5db;
        }

        th {
          padding: 1rem;
          text-align: left;
          font-weight: 600;
          color: #374151;
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        tbody tr {
          border-bottom: 1px solid #e5e7eb;
          transition: background-color 0.2s;

          &:hover {
            background-color: #f9fafb;
          }

          &:last-child {
            border-bottom: none;
          }
        }

        td {
          padding: 1rem;
          font-size: 0.9375rem;
        }

        .rank-col {
          width: 80px;
        }

        .player-col {
          flex: 1;
        }

        .score-col {
          width: 120px;
          text-align: right;
        }

        .games-col {
          width: 100px;
          text-align: center;
        }

        .percentile-col {
          width: 120px;
          text-align: right;
        }

        .rank-badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 40px;
          height: 40px;
          background-color: #3b82f6;
          color: white;
          border-radius: 50%;
          font-weight: 700;
          font-size: 1rem;
        }

        .rank-badge.rank-1 {
          background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
          color: #78350f;
        }

        .rank-badge.rank-2 {
          background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
          color: #374151;
        }

        .rank-badge.rank-3 {
          background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
          color: white;
        }

        .player-link {
          color: #3b82f6;
          text-decoration: none;
          font-weight: 500;

          &:hover {
            text-decoration: underline;
          }
        }

        .score-value {
          color: #10b981;
          font-weight: 600;
        }

        @media (max-width: 768px) {
          .leaderboard-controls {
            flex-direction: column;
            align-items: flex-start;
          }

          .stats {
            width: 100%;
            justify-content: space-between;
          }

          th,
          td {
            padding: 0.75rem 0.5rem;
            font-size: 0.875rem;
          }

          .rank-col {
            width: 60px;
          }

          .rank-badge {
            width: 32px;
            height: 32px;
            font-size: 0.875rem;
          }

          .score-col,
          .percentile-col {
            width: auto;
            text-align: left;
          }
        }
      `}</style>
    </div>
  );
}
