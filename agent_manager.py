#!/usr/bin/env python3
"""
Iteration Manager — Multi-Agent Orchestrator
=============================================
Orchestrates the agent team, manages RAM under 6GB, tracks discoveries,
and iterates forever (or until stopped).

Agent Team:
1. Moonshot Agent — Millennium Prize problems exploration
2. Zeta Agent — Riemann zeta function connections  
3. Cross-Domain Agent — Applications in other fields
4. Compression Agent — Supernatural compression codecs

RAM Management:
- Total budget: 5500 MB (safe margin under 6GB)
- Per-agent budget: 1000 MB
- Manager overhead: 500 MB
- Aggressive GC between agent runs

Features:
- Round-robin agent execution
- Discovery consolidation and deduplication
- Automatic report generation
- Memory monitoring and recovery
- Checkpoint/save state
- Iteration logging
"""

import gc
import sys
import time
import json
import math
import random
import tracemalloc
import subprocess
import signal
import os
from datetime import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path

# Import agents
try:
    from agent_moonshot import MoonshotAgent, MoonshotDiscovery
    from agent_zeta import RiemannZetaAgent, ZetaDiscovery
    from agent_cross_domain import CrossDomainAgent, CrossDomainDiscovery
    from agent_compression import SupernaturalCompressionAgent, CompressionDiscovery
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import agents: {e}")
    AGENTS_AVAILABLE = False

# ──────────────────────────────────────────────────────────────────────
# Memory Management
# ──────────────────────────────────────────────────────────────────────

def get_memory_mb():
    """Get current memory usage in MB."""
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except:
        return 0

def get_system_memory():
    """Get total system memory info (Linux)."""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        
        mem_info = {}
        for line in lines:
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().replace('kB', '').strip()
                mem_info[key] = int(val) // 1024  # Convert to MB
        
        return {
            'total': mem_info.get('MemTotal', 0),
            'free': mem_info.get('MemFree', 0),
            'available': mem_info.get('MemAvailable', 0),
            'used': mem_info.get('MemTotal', 0) - mem_info.get('MemFree', 0)
        }
    except:
        return {}

def aggressive_gc():
    """Aggressive garbage collection."""
    gc.collect()
    gc.collect()
    gc.collect()
    
    # Clear gmpy2 cache if available
    try:
        import gmpy2
        gmpy2.get_context().clear_cache()
    except:
        pass
    
    # Force Python memory allocator to release memory
    try:
        import ctypes
        ctypes.CDLL(None).malloc_trim(0)
    except:
        pass

def check_memory_limit(limit_mb=5500):
    """Check if under memory limit."""
    current = get_memory_mb()
    return current < limit_mb

# ──────────────────────────────────────────────────────────────────────
# Discovery Consolidation
# ──────────────────────────────────────────────────────────────────────

@dataclass
class UnifiedDiscovery:
    """Unified discovery format across all agents."""
    id: str
    source_agent: str
    category: str
    title: str
    description: str
    confidence: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    related_theorems: List[str] = field(default_factory=list)
    verified: bool = False
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_moonshot(cls, d: MoonshotDiscovery, idx: int):
        return cls(
            id=f"MOON_{idx:04d}",
            source_agent="moonshot",
            category=d.problem,
            title=d.hypothesis[:100],
            description=d.hypothesis,
            confidence=d.confidence,
            metadata={'field': d.mathematical_field, 'experiment': d.experiment_id},
            related_theorems=[],
            verified=False
        )
    
    @classmethod
    def from_zeta(cls, d: ZetaDiscovery, idx: int):
        return cls(
            id=f"ZETA_{idx:04d}",
            source_agent="zeta",
            category=d.field,
            title=d.title,
            description=d.statement,
            confidence=d.confidence,
            metadata={'experiment': d.experiment_id, 'theorem_id': d.theorem_id},
            related_theorems=d.related_theorems,
            verified=False
        )
    
    @classmethod
    def from_cross_domain(cls, d: CrossDomainDiscovery, idx: int):
        return cls(
            id=f"CROSS_{idx:04d}",
            source_agent="cross_domain",
            category=d.domain,
            title=d.application,
            description=d.ppt_connection,
            confidence=d.confidence,
            metadata={'feasibility': d.feasibility, 'experiment': d.experiment_id},
            related_theorems=[d.theorem_id] if d.theorem_id else [],
            verified=False
        )
    
    @classmethod
    def from_compression(cls, d: CompressionDiscovery, idx: int):
        return cls(
            id=f"COMP_{idx:04d}",
            source_agent="compression",
            category="Compression",
            title=d.approach,
            description=d.description,
            confidence=0.8,  # Default for compression
            metadata={
                'ratio': d.compression_ratio,
                'speed': d.speed_mb_s,
                'quality': d.quality,
                'best_for': d.best_for,
                'theorem': d.theorem_id,
                'experiment': d.experiment_id
            },
            related_theorems=[d.theorem_id] if d.theorem_id else [],
            verified=False
        )


class DiscoveryDatabase:
    """Centralized discovery storage and management."""
    
    def __init__(self):
        self.discoveries: List[UnifiedDiscovery] = []
        self.by_category = defaultdict(list)
        self.by_agent = defaultdict(list)
        self.high_confidence = []  # confidence > 0.8
        self.verified = []
        self.stats = {
            'total': 0,
            'by_agent': Counter(),
            'by_category': Counter(),
            'avg_confidence': 0
        }
    
    def add(self, discovery: UnifiedDiscovery):
        """Add discovery to database."""
        self.discoveries.append(discovery)
        self.by_category[discovery.category].append(discovery)
        self.by_agent[discovery.source_agent].append(discovery)
        
        if discovery.confidence > 0.8:
            self.high_confidence.append(discovery)
        if discovery.verified:
            self.verified.append(discovery)
        
        self._update_stats()
    
    def add_batch(self, discoveries: List[UnifiedDiscovery]):
        """Add multiple discoveries."""
        for d in discoveries:
            self.add(d)
    
    def _update_stats(self):
        """Update statistics."""
        self.stats['total'] = len(self.discoveries)
        self.stats['by_agent'] = Counter(d.source_agent for d in self.discoveries)
        self.stats['by_category'] = Counter(d.category for d in self.discoveries)
        
        if self.discoveries:
            self.stats['avg_confidence'] = sum(d.confidence for d in self.discoveries) / len(self.discoveries)
    
    def get_top(self, n=20):
        """Get top N discoveries by confidence."""
        return sorted(self.discoveries, key=lambda d: d.confidence, reverse=True)[:n]
    
    def get_by_agent(self, agent: str):
        """Get discoveries from specific agent."""
        return self.by_agent.get(agent, [])
    
    def get_by_category(self, category: str):
        """Get discoveries in category."""
        return self.by_category.get(category, [])
    
    def to_dict(self):
        """Export to dictionary."""
        return {
            'discoveries': [d.to_dict() for d in self.discoveries],
            'stats': dict(self.stats),
            'high_confidence_count': len(self.high_confidence),
            'verified_count': len(self.verified)
        }
    
    def save(self, filepath: str):
        """Save to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load(self, filepath: str):
        """Load from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.discoveries = []
        self.by_category = defaultdict(list)
        self.by_agent = defaultdict(list)
        self.high_confidence = []
        self.verified = []
        
        for d_data in data.get('discoveries', []):
            d = UnifiedDiscovery(**d_data)
            self.add(d)
        
        self.stats = data.get('stats', {})
    
    def generate_report(self):
        """Generate human-readable report."""
        lines = []
        lines.append("=" * 78)
        lines.append("DISCOVERY DATABASE REPORT")
        lines.append("=" * 78)
        lines.append(f"Total discoveries: {self.stats['total']}")
        lines.append(f"Average confidence: {self.stats['avg_confidence']:.2%}")
        lines.append(f"High confidence (>80%): {len(self.high_confidence)}")
        lines.append(f"Verified: {len(self.verified)}")
        lines.append("")
        
        lines.append("By Agent:")
        for agent, count in self.stats['by_agent'].items():
            lines.append(f"  {agent}: {count}")
        lines.append("")
        
        lines.append("By Category:")
        for cat, count in self.stats['by_category'].items():
            lines.append(f"  {cat}: {count}")
        lines.append("")
        
        lines.append("Top 10 Discoveries:")
        for i, d in enumerate(self.get_top(10), 1):
            lines.append(f"\n{i}. [{d.id}] {d.title}")
            lines.append(f"   Agent: {d.source_agent} | Confidence: {d.confidence:.1%}")
            lines.append(f"   {d.description[:100]}...")
        
        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# Iteration Manager
# ──────────────────────────────────────────────────────────────────────

class IterationManager:
    """
    Main iteration manager and orchestrator.
    Runs agents in cycles, manages memory, consolidates discoveries.
    """
    
    def __init__(self, memory_limit_mb=5500, checkpoint_dir="agent_checkpoints"):
        self.memory_limit = memory_limit_mb
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        self.discovery_db = DiscoveryDatabase()
        self.iteration = 0
        self.start_time = time.time()
        
        # Initialize agents
        self.agents = {}
        self.agent_status = {}
        
        if AGENTS_AVAILABLE:
            self._init_agents()
        
        self.log_file = self.checkpoint_dir / "iteration_log.jsonl"
    
    def _init_agents(self):
        """Initialize all agents with memory limits."""
        agent_memory = 1000  # MB per agent
        
        self.agents = {
            'moonshot': MoonshotAgent(memory_limit_mb=agent_memory),
            'zeta': RiemannZetaAgent(memory_limit_mb=agent_memory),
            'cross_domain': CrossDomainAgent(memory_limit_mb=agent_memory),
            'compression': SupernaturalCompressionAgent(memory_limit_mb=agent_memory)
        }
        
        self.agent_status = {
            name: {'status': 'ready', 'last_run': None, 'discoveries': 0}
            for name in self.agents
        }
    
    def log_iteration(self, data: Dict):
        """Log iteration data to JSONL file."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(data) + "\n")
    
    def run_agent_cycle(self, agent_name: str):
        """Run one cycle of a specific agent."""
        if agent_name not in self.agents:
            print(f"[!] Agent {agent_name} not found")
            return []
        
        agent = self.agents[agent_name]
        print(f"\n{'='*78}")
        print(f"Running: {agent_name.upper()} AGENT")
        print(f"{'='*78}")
        
        # Check memory before running
        if not check_memory_limit(self.memory_limit * 0.9):
            print(f"[!] Memory limit approaching, running GC...")
            aggressive_gc()
            time.sleep(1)
        
        start_time = time.time()
        
        try:
            # Run agent cycle
            if hasattr(agent, 'start_tracking'):
                agent.start_tracking()
            
            discoveries = agent.run_cycle()
            
            elapsed = time.time() - start_time
            
            # Convert discoveries to unified format
            unified = []
            for i, d in enumerate(discoveries):
                if agent_name == 'moonshot':
                    ud = UnifiedDiscovery.from_moonshot(d, len(self.discovery_db.discoveries) + i + 1)
                elif agent_name == 'zeta':
                    ud = UnifiedDiscovery.from_zeta(d, len(self.discovery_db.discoveries) + i + 1)
                elif agent_name == 'cross_domain':
                    ud = UnifiedDiscovery.from_cross_domain(d, len(self.discovery_db.discoveries) + i + 1)
                elif agent_name == 'compression':
                    ud = UnifiedDiscovery.from_compression(d, len(self.discovery_db.discoveries) + i + 1)
                else:
                    continue
                unified.append(ud)
            
            # Update status
            self.agent_status[agent_name]['last_run'] = time.time()
            self.agent_status[agent_name]['discoveries'] += len(discoveries)
            self.agent_status[agent_name]['status'] = 'success'
            
            # Log
            self.log_iteration({
                'iteration': self.iteration,
                'agent': agent_name,
                'discoveries': len(discoveries),
                'elapsed': elapsed,
                'memory_mb': get_memory_mb()
            })
            
            print(f"[✓] {agent_name}: {len(discoveries)} discoveries in {elapsed:.1f}s")
            
            return unified
            
        except Exception as e:
            print(f"[!] Error running {agent_name}: {e}")
            self.agent_status[agent_name]['status'] = 'error'
            
            import traceback
            traceback.print_exc()
            
            return []
    
    def run_full_cycle(self):
        """Run all agents in round-robin fashion."""
        self.iteration += 1
        print(f"\n{'='*78}")
        print(f"ITERATION MANAGER — Full Cycle {self.iteration}")
        print(f"{'='*78}")
        print(f"Started: {datetime.now().isoformat()}")
        print(f"Memory: {get_memory_mb():.1f} MB / {self.memory_limit} MB limit")
        
        cycle_start = time.time()
        all_discoveries = []
        
        # Run each agent
        agent_order = ['moonshot', 'zeta', 'cross_domain', 'compression']
        
        for agent_name in agent_order:
            # Check total memory
            if not check_memory_limit(self.memory_limit):
                print(f"\n[!] Total memory limit reached, stopping cycle")
                aggressive_gc()
                break
            
            discoveries = self.run_agent_cycle(agent_name)
            all_discoveries.extend(discoveries)
            
            # Aggressive GC between agents
            aggressive_gc()
            time.sleep(0.5)
        
        # Add all discoveries to database
        self.discovery_db.add_batch(all_discoveries)
        
        cycle_elapsed = time.time() - cycle_start
        
        print(f"\n{'='*78}")
        print(f"CYCLE {self.iteration} SUMMARY")
        print(f"{'='*78}")
        print(f"New discoveries: {len(all_discoveries)}")
        print(f"Total discoveries: {len(self.discovery_db.discoveries)}")
        print(f"Cycle time: {cycle_elapsed:.1f}s")
        print(f"Memory: {get_memory_mb():.1f} MB")
        
        # Save checkpoint
        self.save_checkpoint()
        
        return all_discoveries
    
    def save_checkpoint(self):
        """Save current state to checkpoint."""
        # Save discovery database
        self.discovery_db.save(self.checkpoint_dir / "discoveries.json")
        
        # Save agent status
        status_data = {
            'iteration': self.iteration,
            'start_time': self.start_time,
            'agent_status': self.agent_status,
            'timestamp': time.time()
        }
        with open(self.checkpoint_dir / "status.json", 'w') as f:
            json.dump(status_data, f, indent=2)
        
        print(f"[✓] Checkpoint saved")
    
    def load_checkpoint(self):
        """Load state from checkpoint."""
        disc_file = self.checkpoint_dir / "discoveries.json"
        status_file = self.checkpoint_dir / "status.json"
        
        if disc_file.exists():
            self.discovery_db.load(str(disc_file))
            print(f"[✓] Loaded {len(self.discovery_db.discoveries)} discoveries")
        
        if status_file.exists():
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            self.iteration = status_data.get('iteration', 0)
            self.start_time = status_data.get('start_time', time.time())
            self.agent_status = status_data.get('agent_status', {})
            print(f"[✓] Restored iteration {self.iteration}")
    
    def generate_report(self):
        """Generate comprehensive report."""
        report = []
        
        # Header
        report.append("=" * 78)
        report.append("MULTI-AGENT RESEARCH TEAM — COMPREHENSIVE REPORT")
        report.append("=" * 78)
        
        elapsed = time.time() - self.start_time
        report.append(f"Runtime: {elapsed/3600:.1f} hours")
        report.append(f"Iterations: {self.iteration}")
        report.append(f"Total discoveries: {len(self.discovery_db.discoveries)}")
        report.append("")
        
        # Agent status
        report.append("AGENT STATUS:")
        report.append("-" * 40)
        for name, status in self.agent_status.items():
            report.append(f"  {name}: {status['discoveries']} discoveries, status={status['status']}")
        report.append("")
        
        # Discovery database report
        report.append(self.discovery_db.generate_report())
        report.append("")
        
        # Memory info
        sys_mem = get_system_memory()
        if sys_mem:
            report.append("SYSTEM MEMORY:")
            report.append(f"  Total: {sys_mem.get('total', 0)} MB")
            report.append(f"  Used: {sys_mem.get('used', 0)} MB")
            report.append(f"  Available: {sys_mem.get('available', 0)} MB")
        
        return "\n".join(report)
    
    def save_report(self, filename="research_report.md"):
        """Save report to file."""
        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)
        print(f"[✓] Report saved to {filename}")
    
    def run_forever(self, max_iterations=None, max_hours=None):
        """
        Run agent cycles forever (or until limits).
        
        Args:
            max_iterations: Stop after N iterations (None = unlimited)
            max_hours: Stop after N hours (None = unlimited)
        """
        print("\n" + "="*78)
        print("MULTI-AGENT RESEARCH TEAM — STARTING")
        print("="*78)
        print(f"Memory limit: {self.memory_limit} MB")
        print(f"Max iterations: {max_iterations or 'unlimited'}")
        print(f"Max hours: {max_hours or 'unlimited'}")
        print(f"Checkpoint dir: {self.checkpoint_dir}")
        print("\nPress Ctrl+C to stop and save...")
        time.sleep(2)
        
        start_time = time.time()
        
        try:
            while True:
                # Check limits
                if max_iterations and self.iteration >= max_iterations:
                    print(f"\n[✓] Reached {max_iterations} iterations")
                    break
                
                if max_hours and (time.time() - start_time) / 3600 >= max_hours:
                    print(f"\n[✓] Reached {max_hours} hour limit")
                    break
                
                # Run cycle
                self.run_full_cycle()
                
                # Print status
                print("\n" + self.discovery_db.generate_report())
                
                # Brief pause between cycles
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n[!] Interrupted by user")
        
        finally:
            # Save final state
            self.save_checkpoint()
            self.save_report()
            
            print("\n" + "="*78)
            print("FINAL STATUS")
            print("="*78)
            print(f"Total iterations: {self.iteration}")
            print(f"Total discoveries: {len(self.discovery_db.discoveries)}")
            print(f"Runtime: {(time.time() - start_time)/3600:.1f} hours")
            print(f"Checkpoint saved to: {self.checkpoint_dir}")
            print(f"Report saved to: research_report.md")


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent Research Iteration Manager")
    parser.add_argument('--mode', choices=['single', 'forever', 'report'], default='single',
                       help='Run mode: single cycle, forever, or just generate report')
    parser.add_argument('--iterations', type=int, default=None, help='Max iterations (for forever mode)')
    parser.add_argument('--hours', type=float, default=None, help='Max hours (for forever mode)')
    parser.add_argument('--memory-limit', type=int, default=5500, help='Memory limit in MB')
    parser.add_argument('--checkpoint-dir', type=str, default='agent_checkpoints', help='Checkpoint directory')
    parser.add_argument('--load-checkpoint', action='store_true', help='Load from checkpoint')
    parser.add_argument('--output', type=str, default='research_report.md', help='Report output file')
    
    args = parser.parse_args()
    
    # Create manager
    manager = IterationManager(
        memory_limit_mb=args.memory_limit,
        checkpoint_dir=args.checkpoint_dir
    )
    
    # Load checkpoint if requested
    if args.load_checkpoint:
        manager.load_checkpoint()
    
    if args.mode == 'single':
        # Run single full cycle
        manager.run_full_cycle()
        manager.save_report(args.output)
        
    elif args.mode == 'forever':
        # Run forever (with optional limits)
        manager.run_forever(max_iterations=args.iterations, max_hours=args.hours)
        
    elif args.mode == 'report':
        # Just generate report from checkpoint
        manager.load_checkpoint()
        print(manager.generate_report())
        manager.save_report(args.output)
    
    print(f"\n[Done] Memory: {get_memory_mb():.1f} MB")
