#!/usr/bin/env python3
"""
Performance and stress tests for chore system.
"""

import unittest
import tempfile
import os
import sys
import time
import threading

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chore import Chore, ChoreStatus
from chore_repository import ChoreRepository
from tmux_window_manager import TMUXWindowManager


class TestPerformance(unittest.TestCase):
    """Test system performance under load."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "perf_test.jsonl")
        self.repo = ChoreRepository(self.test_file)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_bulk_chore_creation(self):
        """Test creating many chores."""
        start_time = time.time()
        chores = []
        
        for i in range(100):
            chore = self.repo.create(f"Bulk test {i}", f"Description {i}")
            chores.append(chore)
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(len(chores), 100)
        self.assertLess(duration, 5.0)  # Should complete in under 5 seconds
        print(f"Created 100 chores in {duration:.2f} seconds")
    
    def test_large_file_handling(self):
        """Test handling large chore files."""
        # Create many chores
        for i in range(500):
            self.repo.create(f"Large test {i}", f"Description {i}")
        
        # Test reading performance
        start_time = time.time()
        chores = self.repo.list_all()
        end_time = time.time()
        
        self.assertEqual(len(chores), 500)
        self.assertLess(end_time - start_time, 2.0)  # Should read in under 2 seconds
        print(f"Read 500 chores in {end_time - start_time:.2f} seconds")
    
    def test_concurrent_access(self):
        """Test concurrent repository access."""
        def create_chores(thread_id):
            for i in range(10):
                self.repo.create(f"Thread {thread_id} chore {i}", f"Description {i}")
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_chores, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        chores = self.repo.list_all()
        self.assertEqual(len(chores), 50)  # 5 threads * 10 chores each


class TestStress(unittest.TestCase):
    """Stress tests for system limits."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "stress_test.jsonl")
        self.repo = ChoreRepository(self.test_file)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_memory_usage(self):
        """Test memory usage with many chores."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create many chores
        chores = []
        for i in range(1000):
            chore = self.repo.create(f"Memory test {i}", f"Description {i}")
            chores.append(chore)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for 1000 chores)
        self.assertLess(memory_increase, 50 * 1024 * 1024)
        print(f"Memory increase for 1000 chores: {memory_increase / 1024 / 1024:.2f} MB")
    
    def test_file_size_limits(self):
        """Test handling of large file sizes."""
        # Create chores with large descriptions
        large_description = "X" * 10000  # 10KB description
        
        for i in range(100):
            self.repo.create(f"Large desc {i}", large_description)
        
        # Verify file operations still work
        chores = self.repo.list_all()
        self.assertEqual(len(chores), 100)
        
        # Check file size
        file_size = os.path.getsize(self.test_file)
        print(f"File size with large descriptions: {file_size / 1024 / 1024:.2f} MB")
        self.assertGreater(file_size, 1024 * 1024)  # Should be > 1MB


class TestTMUXStress(unittest.TestCase):
    """Stress tests for TMUX integration."""
    
    def test_tmux_availability(self):
        """Test TMUX availability under stress."""
        manager = TMUXWindowManager("stress_test")
        
        # Multiple rapid session checks
        for i in range(100):
            result = manager.has_existing_session()
            self.assertIsInstance(result, bool)
    
    def test_window_operations_stress(self):
        """Test window operations under stress."""
        manager = TMUXWindowManager("stress_test")
        
        # Multiple window listings
        for i in range(50):
            windows = manager.list_chore_windows()
            self.assertIsInstance(windows, list)


if __name__ == '__main__':
    # Skip performance tests if psutil not available
    try:
        import psutil
        unittest.main(verbosity=2)
    except ImportError:
        print("Skipping performance tests - psutil not available")
        # Run only basic stress tests
        suite = unittest.TestSuite()
        suite.addTest(TestStress('test_file_size_limits'))
        suite.addTest(TestTMUXStress('test_tmux_availability'))
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
