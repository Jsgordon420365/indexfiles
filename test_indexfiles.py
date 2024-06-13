import unittest
from indexfiles import inventory_files

class TestInventoryFiles(unittest.TestCase):
    def test_inventory_files(self):
        # Test case 1: Empty root directory
        root_dir = "/path/to/empty/directory"
        exclude_dirs = []
        expected_result = []
        self.assertEqual(inventory_files(root_dir, exclude_dirs), expected_result)

        # Test case 2: Root directory with files and subdirectories
        root_dir = "/path/to/root/directory"
        exclude_dirs = []
        expected_result = [
            {"path": "/path/to/root/directory/file1.txt", "size": 100, "creation_time": "Mon Jan 1 00:00:00 2022", "modification_time": "Tue Jan 2 00:00:00 2022"},
            {"path": "/path/to/root/directory/file2.txt", "size": 200, "creation_time": "Wed Jan 3 00:00:00 2022", "modification_time": "Thu Jan 4 00:00:00 2022"},
            {"path": "/path/to/root/directory/subdirectory/file3.txt", "size": 300, "creation_time": "Fri Jan 5 00:00:00 2022", "modification_time": "Sat Jan 6 00:00:00 2022"}
        ]
        self.assertEqual(inventory_files(root_dir, exclude_dirs), expected_result)

        # Test case 3: Root directory with excluded directories
        root_dir = "/path/to/root/directory"
        exclude_dirs = ["subdirectory"]
        expected_result = [
            {"path": "/path/to/root/directory/file1.txt", "size": 100, "creation_time": "Mon Jan 1 00:00:00 2022", "modification_time": "Tue Jan 2 00:00:00 2022"},
            {"path": "/path/to/root/directory/file2.txt", "size": 200, "creation_time": "Wed Jan 3 00:00:00 2022", "modification_time": "Thu Jan 4 00:00:00 2022"}
        ]
        self.assertEqual(inventory_files(root_dir, exclude_dirs), expected_result)

if __name__ == '__main__':
    unittest.main()