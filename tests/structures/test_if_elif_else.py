from ..utils import TranspileTestCase


class IfElifElseTests(TranspileTestCase):
    def test_if(self):
        # Matches if
        self.assertCodeExecution("""
            x = 1
            if x < 5:
                print('Small x')
            print('Done.')
            """)

        # No match on if
        self.assertCodeExecution("""
            x = 10
            if x < 5:
                print('Small x')
            print('Done.')
            """)

    def test_if_else(self):
        self.assertCodeExecution("""
            x = 1
            if x < 5:
                print('Small x')
            else:
                print('Large x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 10
            if x < 5:
                print('Small x')
            else:
                print('Large x')
            print('Done.')
            """)

    def test_if_elif_else(self):
        self.assertCodeExecution("""
            x = 1
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            else:
                print('Large x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 10
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            else:
                print('Large x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 100
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            else:
                print('Large x')
            print('Done.')
            """)

    def test_if_elif_elif_else(self):
        self.assertCodeExecution("""
            x = 1
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            elif x < 500:
                print('Large x')
            else:
                print('Huge x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 10
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            elif x < 500:
                print('Large x')
            else:
                print('Huge x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 100
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            elif x < 500:
                print('Large x')
            else:
                print('Huge x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 1000
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            elif x < 500:
                print('Large x')
            else:
                print('Huge x')
            print('Done.')
            """)

    def test_if_elif_elif(self):
        self.assertCodeExecution("""
            x = 1
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            elif x < 500:
                print('Large x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 10
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            elif x < 500:
                print('Large x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 100
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            elif x < 500:
                print('Large x')
            print('Done.')
            """)

        self.assertCodeExecution("""
            x = 1000
            if x < 5:
                print('Small x')
            elif x < 50:
                print('Medium x')
            elif x < 500:
                print('Large x')
            print('Done.')
            """)
