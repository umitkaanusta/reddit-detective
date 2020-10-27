from tests import test_data_models, test_relationships

if __name__ == '__main__':
    print("Testing Data Models...")
    test_data_models.run()
    print("Testing Data models - Success!")
    print("Testing Relationships...")
    test_relationships.run()
    print("Testing Relationships - Success!")
