"""Memory Store Module

Stores and manages agent experiences for learning and improvement.
"""

import time
import json
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ExperienceType(Enum):
    """Types of experiences"""
    TASK_EXECUTION = "task_execution"
    ERROR_RECOVERY = "error_recovery"
    USER_INTERACTION = "user_interaction"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    LEARNING_INSIGHT = "learning_insight"

@dataclass
class Experience:
    """Represents a learning experience"""
    experience_id: str
    experience_type: ExperienceType
    context: Dict[str, Any]
    action_taken: str
    outcome: Dict[str, Any]
    success: bool
    confidence: float  # 0.0 to 1.0
    tags: List[str]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if not self.experience_id:
            self.experience_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique experience ID"""
        content = f"{self.experience_type.value}_{self.action_taken}_{self.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

class MemoryStore:
    """Stores and retrieves agent experiences for learning"""
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for memory storage"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Create experiences table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    experience_id TEXT PRIMARY KEY,
                    experience_type TEXT NOT NULL,
                    context TEXT NOT NULL,
                    action_taken TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    confidence REAL NOT NULL,
                    tags TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for faster queries
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_experience_type 
                ON experiences(experience_type)
            """)
            
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON experiences(timestamp)
            """)
            
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_success 
                ON experiences(success)
            """)
            
            self.connection.commit()
            logger.info(f"Memory database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory database: {e}")
            raise
    
    def store_experience(self, experience: Experience) -> bool:
        """Store an experience in memory"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO experiences 
                (experience_id, experience_type, context, action_taken, outcome, 
                 success, confidence, tags, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                experience.experience_id,
                experience.experience_type.value,
                json.dumps(experience.context),
                experience.action_taken,
                json.dumps(experience.outcome),
                experience.success,
                experience.confidence,
                json.dumps(experience.tags),
                experience.timestamp
            ))
            
            self.connection.commit()
            logger.debug(f"Stored experience: {experience.experience_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store experience: {e}")
            return False
    
    def retrieve_experiences(self, 
                           experience_type: Optional[ExperienceType] = None,
                           success_only: bool = False,
                           tags: Optional[List[str]] = None,
                           limit: int = 100,
                           since_timestamp: Optional[float] = None) -> List[Experience]:
        """Retrieve experiences based on criteria"""
        try:
            query = "SELECT * FROM experiences WHERE 1=1"
            params = []
            
            if experience_type:
                query += " AND experience_type = ?"
                params.append(experience_type.value)
            
            if success_only:
                query += " AND success = 1"
            
            if since_timestamp:
                query += " AND timestamp >= ?"
                params.append(since_timestamp)
            
            if tags:
                # Simple tag matching - could be improved with full-text search
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            experiences = []
            for row in cursor.fetchall():
                experience = Experience(
                    experience_id=row[0],
                    experience_type=ExperienceType(row[1]),
                    context=json.loads(row[2]),
                    action_taken=row[3],
                    outcome=json.loads(row[4]),
                    success=bool(row[5]),
                    confidence=row[6],
                    tags=json.loads(row[7]),
                    timestamp=row[8]
                )
                experiences.append(experience)
            
            logger.debug(f"Retrieved {len(experiences)} experiences")
            return experiences
            
        except Exception as e:
            logger.error(f"Failed to retrieve experiences: {e}")
            return []
    
    def find_similar_experiences(self, context: Dict[str, Any], 
                               action: str, 
                               similarity_threshold: float = 0.7) -> List[Experience]:
        """Find experiences similar to given context and action"""
        try:
            all_experiences = self.retrieve_experiences(limit=1000)
            similar_experiences = []
            
            for exp in all_experiences:
                similarity = self._calculate_similarity(context, action, exp)
                if similarity >= similarity_threshold:
                    similar_experiences.append((exp, similarity))
            
            # Sort by similarity score
            similar_experiences.sort(key=lambda x: x[1], reverse=True)
            
            return [exp for exp, _ in similar_experiences[:10]]  # Top 10
            
        except Exception as e:
            logger.error(f"Failed to find similar experiences: {e}")
            return []
    
    def _calculate_similarity(self, context: Dict[str, Any], 
                            action: str, 
                            experience: Experience) -> float:
        """Calculate similarity between current situation and stored experience"""
        similarity_score = 0.0
        
        # Action similarity (simple string matching)
        action_similarity = self._string_similarity(action, experience.action_taken)
        similarity_score += action_similarity * 0.4
        
        # Context similarity
        context_similarity = self._dict_similarity(context, experience.context)
        similarity_score += context_similarity * 0.6
        
        return similarity_score
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using simple word overlap"""
        if not s1 or not s2:
            return 0.0
        
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _dict_similarity(self, d1: Dict[str, Any], d2: Dict[str, Any]) -> float:
        """Calculate dictionary similarity"""
        if not d1 or not d2:
            return 0.0
        
        common_keys = set(d1.keys()).intersection(set(d2.keys()))
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if str(d1[key]).lower() == str(d2[key]).lower():
                matches += 1
        
        return matches / len(common_keys)
    
    def get_success_patterns(self, experience_type: Optional[ExperienceType] = None) -> Dict[str, Any]:
        """Analyze success patterns in stored experiences"""
        try:
            successful_experiences = self.retrieve_experiences(
                experience_type=experience_type,
                success_only=True,
                limit=500
            )
            
            if not successful_experiences:
                return {}
            
            patterns = {
                'total_successes': len(successful_experiences),
                'avg_confidence': sum(exp.confidence for exp in successful_experiences) / len(successful_experiences),
                'common_actions': {},
                'common_contexts': {},
                'common_tags': {}
            }
            
            # Analyze common actions
            action_counts = {}
            for exp in successful_experiences:
                action_counts[exp.action_taken] = action_counts.get(exp.action_taken, 0) + 1
            
            patterns['common_actions'] = dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            
            # Analyze common context keys
            context_keys = {}
            for exp in successful_experiences:
                for key in exp.context.keys():
                    context_keys[key] = context_keys.get(key, 0) + 1
            
            patterns['common_contexts'] = dict(sorted(context_keys.items(), key=lambda x: x[1], reverse=True)[:5])
            
            # Analyze common tags
            tag_counts = {}
            for exp in successful_experiences:
                for tag in exp.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            patterns['common_tags'] = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze success patterns: {e}")
            return {}
    
    def get_failure_patterns(self, experience_type: Optional[ExperienceType] = None) -> Dict[str, Any]:
        """Analyze failure patterns in stored experiences"""
        try:
            failed_experiences = self.retrieve_experiences(
                experience_type=experience_type,
                limit=500
            )
            
            failed_experiences = [exp for exp in failed_experiences if not exp.success]
            
            if not failed_experiences:
                return {}
            
            patterns = {
                'total_failures': len(failed_experiences),
                'avg_confidence': sum(exp.confidence for exp in failed_experiences) / len(failed_experiences),
                'common_failure_actions': {},
                'common_failure_contexts': {},
                'common_failure_outcomes': {}
            }
            
            # Analyze common failure actions
            action_counts = {}
            for exp in failed_experiences:
                action_counts[exp.action_taken] = action_counts.get(exp.action_taken, 0) + 1
            
            patterns['common_failure_actions'] = dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            
            # Analyze common failure outcomes
            outcome_types = {}
            for exp in failed_experiences:
                outcome_key = exp.outcome.get('error_type', 'unknown')
                outcome_types[outcome_key] = outcome_types.get(outcome_key, 0) + 1
            
            patterns['common_failure_outcomes'] = dict(sorted(outcome_types.items(), key=lambda x: x[1], reverse=True)[:5])
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze failure patterns: {e}")
            return {}
    
    def cleanup_old_experiences(self, days_to_keep: int = 30) -> int:
        """Remove experiences older than specified days"""
        try:
            cutoff_timestamp = time.time() - (days_to_keep * 24 * 3600)
            
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM experiences WHERE timestamp < ?",
                (cutoff_timestamp,)
            )
            
            deleted_count = cursor.rowcount
            self.connection.commit()
            
            logger.info(f"Cleaned up {deleted_count} old experiences")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old experiences: {e}")
            return 0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory store statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Total experiences
            cursor.execute("SELECT COUNT(*) FROM experiences")
            total_count = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("SELECT COUNT(*) FROM experiences WHERE success = 1")
            success_count = cursor.fetchone()[0]
            
            # Experience types distribution
            cursor.execute("""
                SELECT experience_type, COUNT(*) 
                FROM experiences 
                GROUP BY experience_type
            """)
            type_distribution = dict(cursor.fetchall())
            
            # Recent activity (last 24 hours)
            recent_timestamp = time.time() - 86400
            cursor.execute(
                "SELECT COUNT(*) FROM experiences WHERE timestamp >= ?",
                (recent_timestamp,)
            )
            recent_count = cursor.fetchone()[0]
            
            stats = {
                'total_experiences': total_count,
                'success_count': success_count,
                'success_rate': success_count / total_count if total_count > 0 else 0,
                'type_distribution': type_distribution,
                'recent_activity_24h': recent_count,
                'database_size_mb': self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}
    
    def export_experiences(self, filepath: str, 
                         experience_type: Optional[ExperienceType] = None,
                         limit: int = 1000):
        """Export experiences to JSON file"""
        try:
            experiences = self.retrieve_experiences(
                experience_type=experience_type,
                limit=limit
            )
            
            data = {
                'experiences': [asdict(exp) for exp in experiences],
                'export_timestamp': time.time(),
                'total_exported': len(experiences)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(experiences)} experiences to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export experiences: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Memory store connection closed")