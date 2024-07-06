import os
import unittest
import logging

import agent_controller

SCREENSHOTS = 'screenshots'
class TestAgentController(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self._controller = agent_controller.AgentController()
        self._testcases = [
            {
                'prompt': 'Ask chatgpt about names of top 5 most influential applied ai authors of 2024 in Bangalore. website: https://chatgpt.com',
                'expected': {
                    'action': 'navigate',
                    'url': 'https://chatgpt.com'
                }
            },
            {
                'screenshot': 'chatgpt.png',
                'prompt': 'Ask chatgpt about names of top 5 most influential applied ai authors of 2024 in Bangalore. website: https://chatgpt.com',
                'expected': {
                    'action': 'type_input',
                    'url': 'Message ChatGPT'
                }
            }
        ]
    def test_workflows(self):
        for testcase in self._testcases[1:2]:
            path = os.path.join(SCREENSHOTS, testcase['screenshot']) if 'screenshot' in testcase else None
            ins = self._controller.next_instruction(path, testcase['prompt'])
            logging.info('ins: %s', ins)
            with self.subTest(msg=f"Test case: {testcase['prompt']}"):
                self.assertEqual(testcase['expected']['action'], ins['action'])
                self.validate_action(ins, testcase['expected'])

    def validate_action(self, ins, expected):

        if ins['action'] == 'type_input':
            self.assertEqual(ins['placeholder'], expected['placeholder'])
        elif ins['action'] == 'navigate':
            self.assertEqual(ins['url'], expected['url'])


if __name__ == '__main__':
    unittest.main()
