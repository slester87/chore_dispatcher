import unittest
import os
from chore import Chore, ChoreStatus
from chore_repository import ChoreRepository


class TestChore(unittest.TestCase):
    def test_chore_creation(self):
        chore = Chore("Test Task", "A test description")
        self.assertEqual(chore.name, "Test Task")
        self.assertEqual(chore.description, "A test description")
        self.assertEqual(chore.status, ChoreStatus.DESIGN)
        self.assertIsNotNone(chore.id)
    
    def test_status_advancement(self):
        chore = Chore("Test")
        self.assertTrue(chore.advance_status())
        self.assertEqual(chore.status, ChoreStatus.DESIGN_REVIEW)
        
        # Advance through all statuses
        for _ in range(7):  # 7 more advances to reach WORK_DONE
            chore.advance_status()
        
        self.assertEqual(chore.status, ChoreStatus.WORK_DONE)
        self.assertFalse(chore.advance_status())  # Can't advance further
    
    def test_chore_chaining(self):
        chore1 = Chore("First")
        chore2 = Chore("Second")
        
        chore1.set_next_chore(chore2)
        self.assertIsNone(chore1.get_next_chore())  # Not complete yet
        
        # Complete chore1
        while not chore1.is_complete():
            chore1.advance_status()
        
        self.assertEqual(chore1.get_next_chore(), chore2)


class TestChoreRepository(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_chores.jsonl"
        self.repo = ChoreRepository(self.test_file)
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_create_and_read(self):
        chore = self.repo.create("Test Task", "Description")
        retrieved = self.repo.read(chore.id)
        
        self.assertEqual(retrieved, chore)
        self.assertEqual(retrieved.name, "Test Task")
    
    def test_update(self):
        chore = self.repo.create("Original")
        
        # Test name update
        updated = self.repo.update(chore.id, name="Updated")
        self.assertEqual(updated.name, "Updated")
        self.assertEqual(updated.status, ChoreStatus.DESIGN)  # Status unchanged
        
        # Test valid status progression using advance_status
        chore.advance_status()  # design -> design_review
        updated = self.repo.update(chore.id, status=chore.status)
        self.assertEqual(updated.status, ChoreStatus.DESIGN_REVIEW)
    
    def test_delete(self):
        chore = self.repo.create("To Delete")
        self.assertTrue(self.repo.delete(chore.id))
        self.assertIsNone(self.repo.read(chore.id))
    
    def test_list_and_filter(self):
        chore1 = self.repo.create("Task 1")
        chore2 = self.repo.create("Task 2")
        
        # Advance chore2 to work status through valid transitions
        chore2.advance_status()  # design -> design_review
        chore2.advance_status()  # design_review -> design_ready
        chore2.advance_status()  # design_ready -> plan
        chore2.advance_status()  # plan -> plan_review
        chore2.advance_status()  # plan_review -> plan_ready
        chore2.advance_status()  # plan_ready -> work
        self.repo.update(chore2.id, status=chore2.status)
        
        all_chores = self.repo.list_all()
        self.assertEqual(len(all_chores), 2)
        
        design_chores = self.repo.find_by_status(ChoreStatus.DESIGN)
        self.assertEqual(len(design_chores), 1)
        self.assertEqual(design_chores[0].id, chore1.id)


if __name__ == '__main__':
    unittest.main()
