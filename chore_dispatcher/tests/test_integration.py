#!/usr/bin/env python3
"""
Integration tests for chore system components.
"""

import unittest
import tempfile
import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chore import Chore, ChoreStatus
from chore_repository import ChoreRepository
from communication_templates import ProgressTemplate, ReviewTemplate


class TestWorkflowIntegration(unittest.TestCase):
    """Test complete workflow integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "integration_test.jsonl")
        self.repo = ChoreRepository(self.test_file)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test complete chore workflow from creation to completion."""
        # Create chore
        chore = self.repo.create("Integration test chore", "Test complete workflow")
        self.assertEqual(chore.status, ChoreStatus.DESIGN)
        
        # Progress through design phase
        progress_info = ProgressTemplate.design_progress(
            "Component-based approach",
            ["Factory Pattern", "Observer Pattern"],
            "Ensures loose coupling"
        )
        
        # Advance to design review
        chore.advance_status()
        self.repo.update(chore.id, status=chore.status, progress_info=progress_info)
        self.assertEqual(chore.status, ChoreStatus.DESIGN_REVIEW)
        
        # Reviewer approval
        review_info = ReviewTemplate.approve("design", "Design meets requirements")
        chore.advance_status()
        self.repo.update(chore.id, status=chore.status, review_info=review_info)
        self.assertEqual(chore.status, ChoreStatus.DESIGN_READY)
        
        # Continue through plan phase
        chore.advance_status()  # design_ready -> plan
        self.assertEqual(chore.status, ChoreStatus.PLAN)
        
        # Verify chore persists correctly
        retrieved = self.repo.read(chore.id)
        self.assertEqual(retrieved.status, ChoreStatus.PLAN)
        self.assertEqual(retrieved.progress_info, progress_info)
        self.assertEqual(retrieved.review_info, review_info)
    
    def test_chore_chaining_workflow(self):
        """Test chore chaining through complete workflow."""
        # Create parent and child chores
        parent = self.repo.create("Parent chore", "Parent description")
        child = self.repo.create("Child chore", "Child description")
        
        # Set up chain
        parent.set_next_chore(child)
        self.repo.update(parent.id, name=parent.name)  # Save chain
        
        # Verify chain exists
        retrieved_parent = self.repo.read(parent.id)
        self.assertIsNotNone(retrieved_parent.next_chore)
        self.assertEqual(retrieved_parent.next_chore.id, child.id)
    
    def test_dual_agent_communication(self):
        """Test Worker/Reviewer communication patterns."""
        chore = self.repo.create("Communication test", "Test dual-agent workflow")
        
        # Worker progress
        worker_progress = ProgressTemplate.work_progress(
            changes=["Implemented feature X", "Added error handling"],
            testing="Unit tests pass, integration tests complete",
            validation="Manual testing successful",
            concerns="Performance optimization needed"
        )
        
        # Update with worker progress
        chore.advance_status()  # design -> design_review
        chore.advance_status()  # design_review -> design_ready
        chore.advance_status()  # design_ready -> plan
        chore.advance_status()  # plan -> plan_review
        chore.advance_status()  # plan_review -> plan_ready
        chore.advance_status()  # plan_ready -> work
        chore.advance_status()  # work -> work_review
        
        self.repo.update(chore.id, status=chore.status, progress_info=worker_progress)
        
        # Reviewer feedback
        reviewer_feedback = ReviewTemplate.conditional(
            "work",
            "Implementation is solid but needs performance optimization",
            ["Add performance benchmarks", "Optimize critical path algorithms"]
        )
        
        self.repo.update(chore.id, review_info=reviewer_feedback)
        
        # Verify communication stored correctly
        retrieved = self.repo.read(chore.id)
        self.assertEqual(retrieved.progress_info, worker_progress)
        self.assertEqual(retrieved.review_info, reviewer_feedback)
        self.assertIn("WORK PROGRESS", retrieved.progress_info)
        self.assertIn("CONDITIONAL APPROVAL", retrieved.review_info)


class TestSystemIntegration(unittest.TestCase):
    """Test system-level integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "system_test.jsonl")
        self.repo = ChoreRepository(self.test_file)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_system_integrity_validation(self):
        """Test system integrity validation."""
        # Create multiple chores
        chore1 = self.repo.create("Test 1", "Description 1")
        chore2 = self.repo.create("Test 2", "Description 2")
        
        # Validate system integrity
        integrity = self.repo.validate_system_integrity()
        self.assertTrue(integrity['valid'])
        self.assertEqual(integrity['active_count'], 2)
        self.assertEqual(integrity['completed_count'], 0)
    
    def test_archival_system(self):
        """Test chore archival system."""
        chore = self.repo.create("Archival test", "Test archival")
        
        # Complete chore (should trigger archival)
        for _ in range(8):  # Advance through all phases to work_done
            chore.advance_status()
            self.repo.update(chore.id, status=chore.status)
        
        # Verify chore is completed
        self.assertEqual(chore.status, ChoreStatus.WORK_DONE)
        
        # System should handle archival
        integrity = self.repo.validate_system_integrity()
        self.assertTrue(integrity['valid'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
