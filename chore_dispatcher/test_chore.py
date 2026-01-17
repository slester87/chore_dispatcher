import unittest
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
        self.repo = ChoreRepository()
    
    def test_create_and_read(self):
        chore = self.repo.create("Test Task", "Description")
        retrieved = self.repo.read(chore.id)
        
        self.assertEqual(retrieved, chore)
        self.assertEqual(retrieved.name, "Test Task")
    
    def test_update(self):
        chore = self.repo.create("Original")
        updated = self.repo.update(chore.id, name="Updated", status=ChoreStatus.PLAN)
        
        self.assertEqual(updated.name, "Updated")
        self.assertEqual(updated.status, ChoreStatus.PLAN)
    
    def test_delete(self):
        chore = self.repo.create("To Delete")
        self.assertTrue(self.repo.delete(chore.id))
        self.assertIsNone(self.repo.read(chore.id))
    
    def test_list_and_filter(self):
        chore1 = self.repo.create("Task 1")
        chore2 = self.repo.create("Task 2")
        chore2.status = ChoreStatus.WORK
        
        all_chores = self.repo.list_all()
        self.assertEqual(len(all_chores), 2)
        
        design_chores = self.repo.find_by_status(ChoreStatus.DESIGN)
        self.assertEqual(len(design_chores), 1)
        self.assertEqual(design_chores[0], chore1)


if __name__ == '__main__':
    unittest.main()
