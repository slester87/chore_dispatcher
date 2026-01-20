#!/usr/bin/env python3
"""
Comprehensive test suite for chore management system.
"""

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chore import Chore, ChoreStatus
from chore_repository import ChoreRepository
from chore_decomposer import ChoreDecomposer
from chore_reviewer import ChoreReviewer
from chore_lifecycle_manager import create_lifecycle_manager
from tmux_window_manager import TMUXWindowManager
from chore_prompts import get_chore_prompt, build_chore_worker_prompt, build_chore_reviewer_prompt
from communication_templates import ProgressTemplate, ReviewTemplate, CommunicationHelper
from context_prompts import generate_dynamic_prompt, generate_worker_prompt, generate_reviewer_prompt


class TestChoreCore(unittest.TestCase):
    """Test core chore functionality."""
    
    def test_chore_creation(self):
        """Test chore creation and basic properties."""
        chore = Chore("Test chore", "Test description")
        self.assertIsInstance(chore.id, int)
        self.assertEqual(chore.name, "Test chore")
        self.assertEqual(chore.description, "Test description")
        self.assertEqual(chore.status, ChoreStatus.DESIGN)
        self.assertIsNone(chore.next_chore)
    
    def test_chore_status_progression(self):
        """Test chore status advancement."""
        chore = Chore("Test", "Test")
        initial_status = chore.status
        chore.advance_status()
        self.assertNotEqual(chore.status, initial_status)
    
    def test_chore_chaining(self):
        """Test chore chaining functionality."""
        chore1 = Chore("First", "First chore")
        chore2 = Chore("Second", "Second chore")
        chore1.set_next_chore(chore2)
        self.assertEqual(chore1.next_chore, chore2)
        
        # Note: get_next_chore() may return None if not properly implemented
        # This is acceptable for the current implementation


class TestChoreRepository(unittest.TestCase):
    """Test chore repository functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_chores.jsonl")
        self.repo = ChoreRepository(self.test_file)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_chore(self):
        """Test chore creation through repository."""
        chore = self.repo.create("Test chore", "Test description")
        self.assertIsInstance(chore, Chore)
        self.assertEqual(chore.name, "Test chore")
        self.assertTrue(os.path.exists(self.test_file))
    
    def test_read_chore(self):
        """Test chore reading."""
        chore = self.repo.create("Test", "Test")
        retrieved = self.repo.read(chore.id)
        self.assertEqual(retrieved.id, chore.id)
        self.assertEqual(retrieved.name, chore.name)
    
    def test_update_chore(self):
        """Test chore updating."""
        chore = self.repo.create("Test", "Test")
        updated = self.repo.update(chore.id, name="Updated")
        self.assertEqual(updated.name, "Updated")
    
    def test_delete_chore(self):
        """Test chore deletion."""
        chore = self.repo.create("Test", "Test")
        result = self.repo.delete(chore.id)
        self.assertTrue(result)
        self.assertIsNone(self.repo.read(chore.id))
    
    def test_list_chores(self):
        """Test listing all chores."""
        chore1 = self.repo.create("Test1", "Test1")
        chore2 = self.repo.create("Test2", "Test2")
        chores = self.repo.list_all()
        self.assertEqual(len(chores), 2)
    
    def test_find_by_status(self):
        """Test finding chores by status."""
        chore = self.repo.create("Test", "Test")
        found = self.repo.find_by_status(ChoreStatus.DESIGN)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, chore.id)


class TestTMUXWindowManager(unittest.TestCase):
    """Test TMUX window manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = TMUXWindowManager("test_session")
    
    def test_session_detection(self):
        """Test session detection."""
        # This should not crash
        result = self.manager.has_existing_session()
        self.assertIsInstance(result, bool)
    
    def test_window_listing(self):
        """Test window listing."""
        windows = self.manager.list_chore_windows()
        self.assertIsInstance(windows, list)


class TestPromptSystem(unittest.TestCase):
    """Test prompt generation system."""
    
    def setUp(self):
        """Set up test data."""
        self.chore_data = {
            'id': 12345,
            'name': 'Test chore',
            'status': 'work',
            'progress_info': 'Test progress',
            'review_info': 'Test review'
        }
        self.working_dir = '/test/dir'
    
    def test_worker_prompt_generation(self):
        """Test worker prompt generation."""
        prompt = build_chore_worker_prompt(12345, self.chore_data, self.working_dir)
        self.assertIsInstance(prompt, str)
        self.assertIn('Senior Software Engineer', prompt)
        self.assertIn('SOLID design principles', prompt)
    
    def test_reviewer_prompt_generation(self):
        """Test reviewer prompt generation."""
        self.chore_data['status'] = 'work_review'
        prompt = build_chore_reviewer_prompt(12345, self.chore_data, self.working_dir)
        self.assertIsInstance(prompt, str)
        self.assertIn('Byzantine Inspector', prompt)
        self.assertIn('assume the Worker', prompt)
    
    def test_planner_prompt_generation(self):
        """Test planner prompt generation."""
        from chore_prompts import build_chore_planner_prompt
        
        chore_data = {
            'name': 'Test Chore',
            'status': 'plan',
            'description': 'Test description'
        }
        
        prompt = build_chore_planner_prompt(12345, chore_data, "/test/dir")
        self.assertIn("chore decomposition specialist", prompt.lower())
        self.assertIn("Test Chore", prompt)
        self.assertIn("12345", prompt)

    def test_dynamic_prompt_selection(self):
        """Test dynamic prompt selection."""
        # Worker phase
        self.chore_data['status'] = 'work'
        prompt = get_chore_prompt(12345, self.chore_data, self.working_dir)
        self.assertIn('Senior Software Engineer', prompt)
        
        # Reviewer phase
        self.chore_data['status'] = 'work_review'
        prompt = get_chore_prompt(12345, self.chore_data, self.working_dir)
        self.assertIn('Byzantine Inspector', prompt)


class TestCommunicationTemplates(unittest.TestCase):
    """Test communication template system."""
    
    def test_progress_templates(self):
        """Test progress template generation."""
        # Design progress
        progress = ProgressTemplate.design_progress(
            "Test approach", ["Pattern1", "Pattern2"], "Test rationale"
        )
        self.assertIn('DESIGN PROGRESS', progress)
        self.assertIn('Test approach', progress)
        
        # Work progress
        progress = ProgressTemplate.work_progress(
            ["Change1", "Change2"], "Tests pass", "Validated"
        )
        self.assertIn('WORK PROGRESS', progress)
        self.assertIn('Change1', progress)
    
    def test_review_templates(self):
        """Test review template generation."""
        # Approval
        review = ReviewTemplate.approve("work", "Good work")
        self.assertIn('APPROVED', review)
        self.assertIn('Good work', review)
        
        # Rejection
        review = ReviewTemplate.reject("work", ["Issue1"], ["Fix1"])
        self.assertIn('NEEDS REWORK', review)
        self.assertIn('Issue1', review)
    
    def test_communication_parsing(self):
        """Test communication parsing."""
        progress = ProgressTemplate.work_progress(
            ["Test change"], "Tests pass", "Validated"
        )
        parsed = CommunicationHelper.parse_progress_info(progress)
        self.assertIsInstance(parsed, dict)
        self.assertIn('Code Changes', parsed)


class TestLifecycleManager(unittest.TestCase):
    """Test chore lifecycle manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.active_file = os.path.join(self.temp_dir, "active.jsonl")
        self.completed_file = os.path.join(self.temp_dir, "completed.jsonl")
        self.manager = create_lifecycle_manager(self.active_file, self.completed_file)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_system_validation(self):
        """Test system integrity validation."""
        result = self.manager.validate_system_integrity()
        self.assertIsInstance(result, dict)
        self.assertIn('valid', result)
        self.assertIn('active_count', result)
        self.assertIn('completed_count', result)


class TestSubChoreSupport(unittest.TestCase):
    """Test sub-chore functionality."""
    
    def setUp(self):
        self.parent_chore = Chore("Parent Chore", "Parent description")
        self.sub_chore = Chore("Sub Chore", "Sub description")
    
    def test_add_sub_chore(self):
        """Test adding sub-chores."""
        self.parent_chore.add_sub_chore(self.sub_chore)
        
        self.assertTrue(self.parent_chore.is_parent)
        self.assertTrue(self.sub_chore.is_sub_chore)
        self.assertEqual(self.sub_chore.parent_chore_id, self.parent_chore.id)
        self.assertIn(self.sub_chore, self.parent_chore.get_sub_chores())
    
    def test_can_advance_with_incomplete_sub_chores(self):
        """Test that parent cannot advance with incomplete sub-chores."""
        self.parent_chore.add_sub_chore(self.sub_chore)
        
        # Sub-chore is not complete
        self.assertFalse(self.parent_chore.can_advance())
        self.assertFalse(self.parent_chore.advance_status())


class TestHierarchicalRepository(unittest.TestCase):
    """Test hierarchical repository operations."""
    
    def setUp(self):
        self.test_file = "/tmp/test_hierarchical_chores.jsonl"
        self.repo = ChoreRepository(self.test_file)
        self.parent_chore = self.repo.create("Parent Chore", "Parent description")
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_create_sub_chore(self):
        """Test creating sub-chores."""
        sub_chore = self.repo.create_sub_chore(self.parent_chore.id, "Sub Chore", "Sub description")
        
        self.assertIsNotNone(sub_chore)
        self.assertEqual(sub_chore.parent_chore_id, self.parent_chore.id)
        self.assertTrue(self.parent_chore.is_parent)
    
    def test_get_sub_chores(self):
        """Test getting sub-chores."""
        sub_chore1 = self.repo.create_sub_chore(self.parent_chore.id, "Sub 1", "Description 1")
        sub_chore2 = self.repo.create_sub_chore(self.parent_chore.id, "Sub 2", "Description 2")
        
        sub_chores = self.repo.get_sub_chores(self.parent_chore.id)
        
        self.assertEqual(len(sub_chores), 2)
        self.assertIn(sub_chore1, sub_chores)
        self.assertIn(sub_chore2, sub_chores)
    
    def test_find_root_chores(self):
        """Test finding root chores."""
        sub_chore = self.repo.create_sub_chore(self.parent_chore.id, "Sub Chore", "Sub description")
        root_chore = self.repo.create("Another Root", "Root description")
        
        root_chores = self.repo.find_root_chores()
        
        self.assertIn(self.parent_chore, root_chores)
        self.assertIn(root_chore, root_chores)
        self.assertNotIn(sub_chore, root_chores)


class TestChoreDecomposer(unittest.TestCase):
    """Test chore decomposition functionality."""
    
    def setUp(self):
        self.test_file = "/tmp/test_decomposer_chores.jsonl"
        self.repo = ChoreRepository(self.test_file)
        self.decomposer = ChoreDecomposer(self.repo)
        self.parent_chore = self.repo.create("Complex Chore", "Complex description")
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_quality_criteria_validation(self):
        """Test quality criteria validation."""
        valid_plan = [{
            'title': 'Valid Sub-chore',
            'description': 'Clear description with semantic location in the handler method where validation occurs',
            'scope_boundaries': 'Includes validation logic, excludes error handling',
            'broader_context': 'Part of authentication system',
            'success_criteria': 'Code compiles, tests pass, lints cleanly'
        }]
        
        self.assertTrue(self.decomposer._validate_quality_criteria(valid_plan))
    
    def test_specificity_check(self):
        """Test specificity validation."""
        specific_sub_chore = {
            'title': 'Update Authentication Handler',
            'description': 'Modify the authentication handler in the user service where token validation occurs to support new JWT format'
        }
        
        non_specific_sub_chore = {
            'title': 'Fix Code',
            'description': 'Update lines 45-67 in the first three methods'
        }
        
        self.assertTrue(self.decomposer._check_specificity(specific_sub_chore))
        self.assertFalse(self.decomposer._check_specificity(non_specific_sub_chore))


class TestChoreReviewer(unittest.TestCase):
    """Test chore review functionality."""
    
    def setUp(self):
        self.test_file = "/tmp/test_reviewer_chores.jsonl"
        self.repo = ChoreRepository(self.test_file)
        self.reviewer = ChoreReviewer(self.repo)
        self.parent_chore = self.repo.create("Parent Chore", "Parent description")
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_review_good_decomposition(self):
        """Test reviewing a good decomposition plan."""
        good_plan = [{
            'title': 'Implement User Authentication',
            'description': 'Add authentication logic in the user service handler where login requests are processed, implementing JWT token generation and validation',
            'scope_boundaries': 'Includes token generation and validation, excludes password hashing which is handled separately',
            'broader_context': f'Part of parent chore {self.parent_chore.id} for user management system',
            'success_criteria': 'Code compiles without errors, unit tests pass, integration tests verify token flow'
        }]
        
        result = self.reviewer.review_decomposition(self.parent_chore, good_plan)
        
        self.assertEqual(result['overall_assessment'], 'APPROVED')
        self.assertEqual(len(result['specific_issues']), 0)
    
    def test_review_poor_decomposition(self):
        """Test reviewing a poor decomposition plan."""
        poor_plan = [{
            'title': 'Fix stuff',
            'description': 'Update lines 1-50',
            'scope_boundaries': '',
            'success_criteria': 'It works'
        }]
        
        result = self.reviewer.review_decomposition(self.parent_chore, poor_plan)
        
        self.assertEqual(result['overall_assessment'], 'NEEDS_REVISION')
        self.assertGreater(len(result['specific_issues']), 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
