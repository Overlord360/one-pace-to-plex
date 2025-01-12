import os, sys
import json
import unittest
from unittest.mock import patch, MagicMock, call

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # look in parent directory for python files

import rename
import Modules.FileIO as FileIO

class TestRenameFunctions(unittest.TestCase):
        
    #unit test for rename.set_mapping()
    def test_set_mapping(self):
        rename.set_mapping("test", "test2")
        self.assertEqual(rename.episode_mapping, "test")
        self.assertEqual(rename.chapter_mapping, "test2")
    
    #unit test for rename.set_ref_file_vars()
    def test_set_ref_file_vars(self):
        rename.set_ref_file_vars("test", "test2")
        self.assertEqual(rename.episodes_ref_file, "test")
        self.assertEqual(rename.chapters_ref_file, "test2")
    
    #unit test for rename.generate_new_name_for_episode()
    def test_generate_new_name_for_episode(self):
        rename.set_ref_file_vars("../episodes-reference.json", "../chapters-reference.json" )
        #map = rename.episode_mapping
        rename.set_mapping(FileIO.load_json_file(rename.episodes_ref_file), FileIO.load_json_file(rename.chapters_ref_file))
        
        filename = "[One Pace][3-5] Romance Dawn 03 [1080p][F5E73C4E].mkv"
        new_name = rename.generate_new_name_for_episode(filename)
        assert new_name=="One.Piece.E2.1080p.mkv"
        
        filename = "[One Pace] Chapter 700-701 [720p][2A35B710].mkv"
        new_name = rename.generate_new_name_for_episode(filename)
        assert new_name=="One.Piece.E628-E630.720p.mkv"
        
        filename = "[One Pace][677-678] Punk Hazard 12 [720p][CD83F1E9].mkv"
        new_name = rename.generate_new_name_for_episode(filename)
        assert new_name=="One.Piece.E603-E604.720p.mkv"
        

class TestFileIOFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.isdir("One Piece [tvdb4-81797]"):
            os.mkdir("One Piece [tvdb4-81797]")
        if not os.path.isdir(os.path.join("One Piece [tvdb4-81797]","test1")):
            os.mkdir(os.path.join("One Piece [tvdb4-81797]","test1"))
    
    @classmethod
    def tearDownClass(cls):
        if os.path.isdir("One Piece [tvdb4-81797]"):
            if os.path.isdir(os.path.join("One Piece [tvdb4-81797]","test1")):
                os.rmdir(os.path.join("One Piece [tvdb4-81797]","test1"))
            os.rmdir("One Piece [tvdb4-81797]")

    
    #unit test for FileIO.hello()
    @patch("Modules.FileIO.print")
    def test_hello(self, mock_print):
        FileIO.hello()
        mock_print.assert_called_once_with("Hello World!")
    
    def test_list_mkv_files_in_directory_invalid_directory(self):
        # test for a directory that doesn't exist
        with self.assertRaises(FileNotFoundError):
            FileIO.list_mkv_files_in_directory("./not-a-directory")

    #unit test for FileIO.load_json_file()
    @patch("Modules.FileIO.print")
    def test_load_json_file(self, mock_print):
        # test episode mapping file
        episode_mapping = json.loads("""{
                                            "Romance Dawn": {
                                                "01": "S00E36",
                                                "02": "E1",
                                                "03": "E2",
                                                "04": "E3"
                                            }
                                        }
                                    """)
        #print current directory
        #print(os.getcwd())
        self.assertEqual(FileIO.load_json_file("./episodes-test.json"), episode_mapping)
        
        # test chapter mapping file
        chapter_mapping = json.loads("""
                                    {
                                        "700-701": "E628-E630",
                                        "702-703": "E631-E633"
                                    }
                                    """)
        self.assertEqual(FileIO.load_json_file("./chapters-test.json"), chapter_mapping)
        
        
        # test for a file that doesn't exist
        with self.assertRaises(FileNotFoundError):
            FileIO.load_json_file("./not-a-json-file.txt")
        
        #test with a file that is not valid json
        #with self.assertRaises(ValueError):
        with patch.object(FileIO, "exit", return_value=None) as mock_exit:
            with self.assertRaises(UnboundLocalError): #required as "episode_mapping" is not defined and exit has been patched
                FileIO.load_json_file("./invalid.json")
            mock_exit.assert_called_once
            mock_print.assert_called_once_with("Failed to load the file \"./invalid.json\": Expecting value: line 1 column 1 (char 0)")
        
    @patch("Modules.FileIO.abspath")
    @patch("Modules.FileIO.listdir")
    @patch("Modules.FileIO.isfile")
    def test_list_mkv_files_in_directory(self,mock_isfile, mock_listdir, mock_abspath):
        mock_isfile.return_value = True
        mock_listdir.return_value = ["test.mkv", "test2.mkv", "test3.txt"]
        #mock_abspath.return_value = 
        
        files = FileIO.list_mkv_files_in_directory("./")
        
        assert mock_listdir.called
        assert mock_abspath.called
        
        mock_abspath.assert_has_calls([call("./test.mkv"), call("./test2.mkv")])
        mock_abspath.assert_called_with("./test2.mkv")
        mock_listdir.assert_called_with("./")
        
        assert len(files) == 2
        
        #self.assertEqual(rename.list_mkv_files_in_directory("./"), ["test.mkv", "test2.mkv"])

    @patch("Modules.FileIO.walk")
    @patch("Modules.FileIO.list_mkv_files_in_directory")
    def test_get_files_from_directories(self, mock_list_mkv, mock_walk):
        mock_list_mkv.return_value = ["test.mkv"]
        mock_walk.return_value = [("./Tests", ("tmp",), ("test.mkv",)),("./Tests/tmp", (), ("test2.mk","test3.mkv"))]
        files = FileIO.get_files_from_directories("./")
        
        assert mock_list_mkv.called_once
        assert mock_walk.called is False
        mock_list_mkv.assert_called_with("./")
        
        files = FileIO.get_files_from_directories("./", recurse=True)
        
        assert mock_walk.called
        assert len(files) == 2

    #unit test for FileIO.get_biggest_number_from_ref()
    def test_get_biggest_number_from_ref(self):
        string = "E1"
        assert FileIO.get_biggest_number_from_ref(string) == 1

        string = "S00E36"
        assert FileIO.get_biggest_number_from_ref(string) == 36

        string = "E628-E630"
        assert FileIO.get_biggest_number_from_ref(string) == 630

        string = ""
        assert FileIO.get_biggest_number_from_ref(string) == -1

        string = None
        assert FileIO.get_biggest_number_from_ref(string) == -1

        string = "invalid_string"
        assert FileIO.get_biggest_number_from_ref(string) == -1

    #unit test for FileIO.get_smallest_number_from_ref()
    def test_get_smallest_number_from_ref(self):
        string = "E1"
        assert FileIO.get_smallest_number_from_ref(string) == 1

        string = "S00E36"
        assert FileIO.get_smallest_number_from_ref(string) == 36

        string = "E628-E630"
        assert FileIO.get_smallest_number_from_ref(string) == 628

        string = ""
        assert FileIO.get_smallest_number_from_ref(string) == 9999

        string = None
        assert FileIO.get_smallest_number_from_ref(string) == 9999

        string = "invalid_string"
        assert FileIO.get_smallest_number_from_ref(string) == 9999
    
    #unit test for FileIO.generate_tvdb()
    @patch("Modules.FileIO.print")
    def test_generate_tvdb(self, mock_print):
        
        with self.assertRaises(FileNotFoundError):
            FileIO.generate_tvdb("./not-a-file.json", dry_run=True)
        
        with self.assertRaises(FileNotFoundError):
            FileIO.generate_tvdb("./not-a-file.json", dry_run=False)
        
        with patch.object(FileIO, "exit", return_value=None) as mock_exit:
            with self.assertRaises(UnboundLocalError): #required as "episode_mapping" is not defined and exit has been patched
                FileIO.generate_tvdb("./invalid.json", dry_run=False)
            mock_exit.assert_called_once
            mock_print.assert_called_with("Failed to load the file \"./invalid.json\": Expecting value: line 1 column 1 (char 0)")

        FileIO.generate_tvdb("./episodes-test.json", dry_run=True)
        #TODO: test that it works with dry_run=False
    
    @patch("Modules.FileIO.shutil.copy")
    @patch("Modules.FileIO.print")
    @patch("Modules.FileIO.sys.stderr.write")
    @patch("Modules.FileIO.sys.stderr.flush")
    def test_copy_tvdb(self, mock_flush, mock_err, mock_print, mock_copy):
        with self.assertRaises(NotADirectoryError):
            FileIO.copy_tvdb("./not-a-directory")
        
        FileIO.copy_tvdb("./", dry_run=True)
        mock_print.assert_called_with('DRYRUN: copy "tvdb4.mapping" -> "./One Piece [tvdb4-81797]\\test1"')
    
    @patch("Modules.FileIO.print")
    @patch("Modules.FileIO.mkdir")
    @patch("Modules.FileIO.sys.stderr.write")
    def test_generate_file_structure(self,mock_err, mock_mkdir, mock_print):
        with self.assertRaises(NotADirectoryError):
            FileIO.generate_file_structure("./not-a-directory")
        
        FileIO.generate_file_structure("./", dry_run=True)
        assert mock_print.called_with("DRYRUN: mkdir \"./One Piece [tvdb4-81797]\\Romance Dawn\"")
        
        FileIO.generate_file_structure("./")
        assert mock_mkdir.called_with("./One Piece [tvdb4-81797]\\Romance Dawn")





if __name__ == '__main__':
    unittest.main()